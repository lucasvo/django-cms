import re
import datetime
import itertools

from django.http import Http404
from django.db import models
from django.conf import settings
from django.utils.dateformat import DateFormat
from django.utils.safestring import mark_safe
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q, get_app
from django.utils import translation, html
from django.contrib.sites.models import Site
from django.contrib.markup.templatetags import markup

from cms import pagecontents
from cms.util import language_list, MetaTag
from cms.conf.global_settings import LANGUAGE_REDIRECT, USE_TINYMCE, POSITIONS
from cms.managers import PageManager, PageSiteManager

# Look if django-tagging is installed, use its TagField and fall back to
# Django's CharField if unavailable.
try:
    tagging = get_app("tagging")
    from tagging.fields import TagField
except ImproperlyConfigured:
    from django.models import CharField as TagField

PROTOCOL_RE = re.compile('^\w+://')

# if getattr(settings, 'CMS_PAGECONTENTS_AUTOREGISTER', False):
#     pagecontents.autoregister()

class Page(models.Model):
    title = models.CharField(_('title'), max_length=200, help_text=_('The title of the page.'))
    slug = models.SlugField(_('slug'), help_text=_('The name of the page that appears in the URL. A slug can contain letters, numbers, underscores or hyphens.'))

    created = models.DateTimeField(null=True, blank=True, default=datetime.datetime.now)
    modified = models.DateTimeField(null=True, blank=True, default=datetime.datetime.now)

    template = models.CharField(max_length=200, null=True, blank=True)
    context = models.CharField(max_length=200, null=True, blank=True, help_text=_('Optional. Dotted path to a python function that receives two arguments (request, context) and can update the context.'))

    is_published = models.BooleanField(_('is published'), default=True, help_text=_('Whether or not the page is accessible from the web.'))
    start_publish_date = models.DateTimeField(_('start publishing'), null=True, blank=True)
    end_publish_date = models.DateTimeField(_('finish publishing'), null=True, blank=True)

    # Navigation
    parent = models.ForeignKey('self', verbose_name=_('Navigation'), null=True, blank=True, help_text=_('The page will be appended inside the chosen category.'))
    position = models.IntegerField()
    in_navigation = models.BooleanField(_('display in navigation'), default=True)

    # Access
    requires_login = models.BooleanField(_('requires login'), help_text=_('If checked, only logged-in users can view the page. Automatically enabled if the parent page requires a login.'))
    
    #(not implemented yet)
    #change_access_level = models.ManyToManyField(Group, verbose_name=_('change access level'), related_name='change_page_set', null=True, blank=True)
    #view_access_level = models.ManyToManyField(Group, verbose_name=_('view access level'), related_name='view_page_set', null=True, blank=True)

    # Override the page URL or redirect the page to another page.
    override_url = models.BooleanField(default=False)
    overridden_url = models.CharField(max_length=200, null=True, blank=True)
    redirect_to = models.ForeignKey('self', null=True, blank=True, related_name='redirected_pages')

    is_editable = models.BooleanField(default=True)

    sites = models.ManyToManyField(Site, null=True, blank=True, default=[settings.SITE_ID], help_text=_('The site(s) the page is accessible at.'))

    objects = PageManager()
    on_site = PageSiteManager('sites')

    class Meta:
        ordering = ('position', 'title',)
        verbose_name = _('page')
        verbose_name_plural = _('pages')

    def __unicode__(self):
        return self.title

    def save(self):
        self.modified = datetime.datetime.now()
        self.overridden_url = self.overridden_url.strip('/ ')
        super(Page, self).save()

    def get_pagecontents(self, *args, **kwargs):
        pagecontents_list = []
        for related_name in pagecontents.get_related_names():
            # get correct name for pagecontent releationmanager
            pagecontent_set = getattr(self, related_name, None)
            if pagecontent_set is None:
                continue
            if kwargs:
                pagecontents_list.append(pagecontent_set.filter(**kwargs))
            else:
                pagecontents_list.append(pagecontent_set.all())
        return pagecontents_list

    def get_content(self, language=None, position=''):
        if not language:
            language = translation.get_language()

        page_content_list = []
        for published_page_contents in itertools.chain(
                *self.get_pagecontents(is_published=True, position=position)):
            page_content = None

            # Determine the PageContent we want to render
            page_contents = published_page_contents.filter(language=language)
            if not page_contents:
                # Use a PageContent in an alternative language
                for alt_language in language_list():
                    if alt_language == language:
                        continue
                    page_contents = published_page_contents.filter(language=alt_language)

            if not page_content:
                continue

            for page_content in page_contents:
                page_content.prepare()
                page_content_list.append(page_content)
        return page_content_list

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

    def on_path(self, path):
        return path in self.get_path()

    def get_absolute_url(self, language=None):
        if self.redirect_to:
            return self.redirect_to.get_absolute_url()

        url = u'/'
        if self.override_url:
            # Check whether it is an absolute URL
            if PROTOCOL_RE.match(self.overridden_url):
                return self.overridden_url

            # The overridden URL is assumed to not have a leading or trailing slash.
            if self.overridden_url:
                return u'%s%s/' % (url, self.overridden_url.strip('/ '))
            else:
                return url

        if LANGUAGE_REDIRECT:
            if not language:
                language = translation.get_language()
            url += u'%s/' % language

        url += u'/'.join([page.slug for page in self.get_path() if page.parent])
        if not url.endswith('/'):
            url += '/'
        return url
    absolute_url = get_absolute_url

    def get_next_position(self):
        children = Page.objects.filter(parent=self).order_by('-position')
        return children and (children[0].position+1) or 1

    def get_descendants(self):
        children = set()
        pages = Page.objects.filter(parent=self)
        for page in pages:
            children.add(page)
            for subpage in page.get_children():
                children.add(subpage)
        return children

    def get_level(self):
        parent = self.parent
        level = 0
        while parent:
            level += 1
            parent = parent.parent
        return level

    def published(self, user):
        return self in Page.on_site.published(user)
    published.boolean = True
    
    def get_meta_tags(self, language=None):
        return ""
        # if not language:
        #     language = translation.get_language()
        # pagecontent_set = self.pagecontent_set.filter(is_published=True, language=language)
        # tags = []
        # tags += [MetaTag(page_content.keywords, 'keywords', lang=page_content.language) 
        #     for page_content in pagecontent_set.filter(is_published=True) if page_content.keywords]
        # tags += [MetaTag(page_content.description, 'description', lang=page_content.language) 
        #     for page_content in pagecontent_set if page_content.description]
        # tags += [MetaTag(page_content.page_topic, 'page_topic', lang=page_content.language) 
        #     for page_content in pagecontent_set if page_content.page_topic]
        # return tags

class BasePageContent(models.Model):
    page = models.ForeignKey(Page, related_name="%(class)s_related", null=True, blank=True)
    
    title = models.CharField(max_length=200, null=True, blank=True, help_text=_('Used in navigation. Leave this empty to use the default title.'))
    slug = models.CharField(_('slug'), max_length=50, null=True, blank=True, help_text=_('Only specify this if you want to give this page content a specific slug.'))
    page_title = models.CharField(max_length=250, null=True, blank=True, help_text=_('Used for page title. Should be no longer than 150 chars.'))
    
    language = models.CharField(max_length=2, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE[:2])
    is_published = models.BooleanField(default=True)
    
    created = models.DateTimeField(null=True, blank=True, default=datetime.datetime.now)
    modified = models.DateTimeField(null=True, blank=True, default=datetime.datetime.now)
    position = models.CharField(max_length=32, null=True, blank=True, choices=[(pos[0], _(pos[1])) for pos in POSITIONS], default=POSITIONS[0][0])
    order = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return u'%s (%s %s %s %s)' % (
            self.title or self.page.title,
            self.get_language_display(),
            self.created,
            self.modified,
            self.is_published and _('published') or _('unpublished')
        )

    class Meta:
        abstract = True

    def save(self):
        self.modified = datetime.datetime.now()
        super(BasePageContent, self).save()
    
    def prepare(self):
        """
        Override in subclass to to do anything to prepare the pagecontent
        """
        raise NotImplemented

class TextPageContent(BasePageContent):
    CONTENT_TYPES = (
        ('html', _('HTML')),
        ('markdown', _('Markdown')),
        ('textile', _('Textile')),
        ('rst', _('reStructuredText')),
        ('text', _('Plain text')),
    )
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPES, default=USE_TINYMCE and 'html' or 'text')
    allow_template_tags = models.BooleanField(default=True)
    template = models.CharField(max_length=200, null=True, blank=True, help_text=_('Only specify this if you want to override the page template.'))

    keywords = TagField(_('keywords'), max_length=250, help_text=_('Comma separated'), null=True, blank=True)
    description = models.TextField(help_text=_('Keep between 150 and 1000 characters long.'), null=True, blank=True)
    page_topic = models.TextField(help_text=_('Keep between 150 and 1000 characters long.'), null=True, blank=True)

    content = models.TextField(null=True, blank=True)
    content_html = models.TextField(null=True, blank=True)

    def save(self):
        # Convert the content to HTML
        if self.content_type == 'html':
            self.content_html = self.content
        elif self.content_type == 'markdown':
            self.content_html = markup.markdown(self.content)
        elif self.content_type == 'textile':
            self.content_html = markup.textile(self.content)
        elif self.content_type == 'rst':
            self.content_html = markup.restructuredtext(self.content)
        else:
            self.content_html = mark_safe(html.linebreaks(html.escape(self.content)))
        super(TextPageContent, self).save()

    def prepare(self):
        # Set the template and title for the page content
        # if they are not set (but don't save them)
        self.title = self.title or self.page.title
        self.template = self.template or self.page.template
        self.slug = self.slug or self.page.slug
        return self

pagecontents.register(TextPageContent)
