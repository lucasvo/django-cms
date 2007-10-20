import datetime

from django.db import models
from django.conf import settings
from django.utils.dateformat import DateFormat
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_unicode

from cms.util import language_list
from cms.cms_global_settings import LANGUAGE_REDIRECT

"""
class Template(models.Model):
    name = models.CharField(max_length=100)
    content = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
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
            raise RootPageDoesNotExist, 'Please create at least one page.'


class Page(models.Model):
    title = models.CharField(max_length=200, core=True)
    slug = models.CharField(max_length=50, null=True, blank=True)

    created = models.DateTimeField(null=True, blank=True)
    modified = models.DateTimeField(null=True, blank=True)

    template = models.CharField(max_length=200, null=True, blank=True)
    context = models.CharField(max_length=200, null=True, blank=True)

    is_published = models.BooleanField(default=True)

    # Navigation
    parent = models.ForeignKey('self', null=True, blank=True)
    position = models.IntegerField()
    in_navigation = models.BooleanField(default=True)

    # TODO
    override_url = models.BooleanField(default=False)
    overriden_url = models.CharField(max_length=200, null=True, blank=True)

    objects = PageManager()

    class Meta:
        ordering = ('position',)

    class Admin:
        list_display = ('title', 'slug', 'is_published', 'created', 'modified', 'parent', 'position', 'in_navigation')
        list_filter = ('is_published',)
        ordering = ('title',)
        search_fields = ('title', 'slug',)

    def __unicode__(self):
        return self.title

    def save(self):
        if not self.id:
            self.created = datetime.datetime.now()
        self.modified = datetime.datetime.now()
        super(Page, self).save()

    def get_content(self, language):
        published_page_contents = self.pagecontent_set.filter(is_published=True)

        page_content = None

        # Determine the PageContent we want to render
        page_contents = published_page_contents.filter(language=language)
        if page_contents:
            page_content = page_contents[0]
        else:
            # Use a PageContent in an alternative language
            for l in language_list():
                page_contents = published_page_contents.filter(language=l)
                if page_contents:
                    page_content = page_contents[0]
                    break


        if not page_content:
            # TODO: What's better?
            # return None
            page_content = PageContent(page=self)

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

    def absolute_url(self):
        return u'/%s'%self.get_absolute_url()

    def get_absolute_url(self):
        if self.override_url:
            return self.overriden_url
        else:
            url = u'/'.join([page.slug for page in self.get_path() if page.parent])
            return url and u'%s/' % url or url

    def get_link(self, language):
        if LANGUAGE_REDIRECT:
            return '/%s/%s' % (language, self.get_absolute_url())
        else:
            return '/%s' % (self.get_absolute_url())

    def get_next_position(self):
        children = Page.objects.filter(parent=self).order_by('-position')
        return children and (children[0].position+1) or 1



class PageContent(models.Model):
    page = models.ForeignKey(Page, edit_inline=models.STACKED)
    language = models.CharField(max_length=2, choices=settings.LANGUAGES, default='', core=True)
    is_published = models.BooleanField(default=True)
    CONTENT_TYPES = (('html', _('HTML')), ('markdown', _('Markdown')), ('text', _('Plain text')))
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPES, default='markdown')
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
