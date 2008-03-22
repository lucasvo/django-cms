import datetime

from django.db import models
from django.conf import settings
from django.utils.dateformat import DateFormat
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_unicode
from django.db.models import Q
from django.utils import translation
from cms.util import language_list
from cms.cms_global_settings import LANGUAGE_REDIRECT, USE_TINYMCE

"""
class Template(models.Model):
    name = models.CharField(max_length=100)
    content = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

    class Admin:
        list_display = ('name', 'created', 'modified')
"""


class RootPageDoesNotExist(Exception):
    pass

class PageManager(models.Manager):
    def hierarchy(self, parent=None):
        if parent:
            filter = self.filter(parent=parent)
        else:
            try:
                root = self.root()
            except RootPageDoesNotExist:
                return []
            return [(root, self.hierarchy(root))]
        return [(page, self.hierarchy(page)) for page in filter]

    def root(self):
        try:
            return self.filter(parent__isnull=True)[0]
        except IndexError:
            raise RootPageDoesNotExist, unicode(_('Please create at least one page.'))

    def published(self):
        return self.filter(
                           Q(is_published=True),
                           Q(start_publish_date__lte=datetime.date.today()) | Q(start_publish_date__isnull=True), 
                           Q(end_publish_date__gte=datetime.date.today()) | Q(end_publish_date__isnull=True),
                           )
    
    def search(self, query, language=None):
        if not query:
            return
        qs = self.published()
        if language:
            qs = qs.filter(
                        Q(title__icontains=query) |
                        Q(pagecontent__language=language) & 
                        (Q(pagecontent__title__icontains=query) |
                        Q(pagecontent__description__icontains=query) |
                        Q(pagecontent__content__icontains=query))
                    )
        else:
            qs = qs.filter(
                        Q(title__icontains=query) |
                        Q(pagecontent__title__icontains=query) |
                        Q(pagecontent__description__icontains=query) |
                        Q(pagecontent__content__icontains=query)
                    )
        return qs.distinct()

class Page(models.Model):
    title = models.CharField(_('title'), max_length=200, help_text=_('The title of the page.'), core=True)
    slug = models.CharField(_('slug'), max_length=50, help_text=_('The name of the page that appears in the URL. A slug can contain letters, numbers, underscores or hyphens.'), prepopulate_from=("title",))

    created = models.DateTimeField(null=True, blank=True)
    modified = models.DateTimeField(null=True, blank=True)

    template = models.CharField(max_length=200, null=True, blank=True)
    context = models.CharField(max_length=200, null=True, blank=True, help_text=_('Optional. Dotted path to a python function that receives two arguments (request, context) and can update the context.'))

    is_published = models.BooleanField(_('is published'), default=True, help_text=_('Whether or not the page is accessible from the web.'))
    start_publish_date = models.DateTimeField(_('start publishing'), null=True, blank=True)
    end_publish_date = models.DateTimeField(_('finish publishing'), null=True, blank=True)

    # Navigation
    parent = models.ForeignKey('self', verbose_name=_('Navigation'), null=True, blank=True, help_text=_('The page will be appended inside the chosen category.'))
    position = models.IntegerField()
    in_navigation = models.BooleanField(_('display in navigation'), default=True)

    # Access (not implemented yet)
    #change_access_level = models.ManyToManyField(Group, verbose_name=_('change access level'), related_name='change_page_set', filter_interface=models.VERTICAL, null=True, blank=True)
    #view_access_level = models.ManyToManyField(Group, verbose_name=_('view access level'), related_name='view_page_set', filter_interface=models.VERTICAL, null=True, blank=True)

    # Override the page URL or redirect the page to another page.
    override_url = models.BooleanField(default=False)
    overridden_url = models.CharField(max_length=200, null=True, blank=True)
    redirect_to = models.ForeignKey('self', null=True, blank=True, related_name='redirected_pages')

    is_editable = models.BooleanField(default=True)

    objects = PageManager()

    class Meta:
        ordering = ('parent', 'position', 'title',)

    class Admin:
        list_display = ('title', 'slug', 'is_published', 'created', 'modified', 'parent', 'position', 'in_navigation')
        list_filter = ('is_published',)
        ordering = ('parent','title',)
        search_fields = ('title', 'slug',)
        if USE_TINYMCE:
            js = ('js/getElementsBySelector.js',
                  'filebrowser/js/AddFileBrowser.js',
            )

    def __unicode__(self):
        return self.title

    def save(self):
        if not self.id:
            self.created = datetime.datetime.now()
        self.modified = datetime.datetime.now()
        super(Page, self).save()

    def get_content(self, language=None, all=False):
        if not language:
            language = translation.get_language()
        published_page_contents = self.pagecontent_set.filter(is_published=True)

        page_content = None

        # Determine the PageContent we want to render
        page_contents = published_page_contents.filter(language=language)
        if page_contents:
            if all:
                page_content = page_contents
            else:
                page_content = page_contents[0]
        else:
            # Use a PageContent in an alternative language
            for alt_language in language_list():
                if alt_language == language:
                    continue
                page_contents = published_page_contents.filter(language=alt_language)
                if page_contents:
                    if all:
                        page_content = page_contents
                    else:
                        page_content = page_contents[0]
                    break


        if not page_content:
            # TODO: What's better?
            # return None
            page_content = PageContent(page=self)
            if all:
                page_content=[PageContent(page=self)]

        if all and page_content:
            for c in page_content:
                c.prepare()
            return page_content
        return page_content.prepare()

    def get_path(self):
        class PathList(list):
            def __unicode__(self):
                return u' > '.join([smart_unicode(page) for page in self])

        path = [self]
        parent = self.parent
        while parent:
            path.append(parent)
            parent = parent.parent
        return PathList(reversed(path))

    def on_path(self, super):
        return super in self.get_path()

    def get_absolute_url(self):
        if self.redirect_to:
            return self.redirect_to.get_absolute_url()

        if self.override_url:
            # The overridden URL is assumed to not have a leading or trailing slash.
            if self.overridden_url:
                return '/%s/' % self.overridden_url
            else:
                return '/'

        url = u'/'.join([page.slug for page in self.get_path() if page.parent])
        return url and u'/%s/' % url or '/' + url
    absolute_url = get_absolute_url

    def get_link(self, language):
        if LANGUAGE_REDIRECT:
            return '/%s%s' % (language, self.get_absolute_url())
        else:
            return '%s' % (self.get_absolute_url())

    def get_next_position(self):
        children = Page.objects.filter(parent=self).order_by('-position')
        return children and (children[0].position+1) or 1

    def get_level(self):
        parent = self.parent
        level = 0
        while parent:
            level += 1
            parent = parent.parent
        return level

    @property
    def smart_title(self):
        return self.get_content().title

    def published(self):
        today = datetime.date.today()
        return bool(self.is_published) and (not self.start_publish_date or self.start_publish_date.date() <= today) and (not self.end_publish_date or self.end_publish_date.date() >= today)
    published.boolean = True

class PageContent(models.Model):
    page = models.ForeignKey(Page, edit_inline=models.STACKED)
    language = models.CharField(max_length=2, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE[:2], core=True)
    is_published = models.BooleanField(default=True)
    CONTENT_TYPES = (('html', _('HTML')), ('markdown', _('Markdown')), ('text', _('Plain text')))
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPES, default=USE_TINYMCE and 'html' or 'markdown')
    allow_template_tags = models.BooleanField(default=True)

    created = models.DateTimeField(null=True, blank=True)
    modified = models.DateTimeField(null=True, blank=True)

    template = models.CharField(max_length=200, null=True, blank=True, help_text=_('Only specify this if you want to override the page template.'))

    title = models.CharField(max_length=200, null=True, blank=True, help_text=_('Leave this empty to use the default title.'))
    description = models.TextField(null=True, blank=True)
    content = models.TextField(core=True)

    def prepare(self):
        # Set the template and title for the page content, if they are not set (but don't save them)
        self.title = self.title or self.page.title
        self.template = self.template or self.page.template

        if not self.description:
            self.description = ''

        return self

    def save(self):
        if not self.id:
            self.created = datetime.datetime.now()
        self.modified = datetime.datetime.now()
        super(PageContent, self).save()

    #class Admin:
    #    pass

    def __unicode__(self):
        created = self.created and (', created: %s' % DateFormat(self.created).format('jS F Y H:i')) or ''
        modified = self.modified and (', modified: %s' % DateFormat(self.modified).format('jS F Y H:i')) or ''
        return u'%s (%s%s%s%s%s)' % (self.title or self.page.title, self.get_language_display(), created, modified, created and ', ' or '', self.is_published and _('published') or _('unpublished'))
