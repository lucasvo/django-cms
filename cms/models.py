import re
import datetime

from django.db import models
from django.conf import settings
from django.utils.dateformat import DateFormat
from django.utils.safestring import mark_safe
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q, get_app
from django.utils import translation
from django.utils.html import linebreaks, escape
from django.contrib.sites.models import Site
from django.contrib.markup.templatetags.markup import markdown, textile, \
                                                      restructuredtext as rst
from cms.util import language_list, MetaTag
from cms.conf.global_settings import LANGUAGE_REDIRECT, USE_TINYMCE, POSITIONS
from cms.managers import PageManager, PageSiteManager

# Look if django-tagging is installed, use its TagField and fall back to
# Django's CharField if unavailable.
try:
    tagging = get_app("tagging")
    from tagging.fields import TagField
except ImproperlyConfigured:
    from django.db.models import CharField as TagField

PROTOCOL_RE = re.compile('^\w+://')

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

    def get_content(self, language=None, all=False, position=''):
        if not language:
            language = translation.get_language()
        published_page_contents = self.pagecontent_set.filter(is_published=True, position=position)

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
                page_content = [PageContent(page=self)]

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

    def on_path(self, path):
        return path in self.get_path()

    def get_absolute_url(self, language=None, nolang=False):
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

        if LANGUAGE_REDIRECT and not nolang:
            if not language:
                language = translation.get_language()
            url += u'%s/' % language

        url += u'/'.join([page.smart_slug for page in self.get_path() if page.parent])
        if not url.endswith('/'):
            url += '/'
        return url
    absolute_url = get_absolute_url

    def get_absolute_url_nolang(self):
        return self.get_absolute_url(None, True)

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

    def smart_title(self):
        return self.get_content().title
    smart_title = property(smart_title)

    def smart_slug(self):
        return self.get_content().slug
    smart_slug = property(smart_slug)

    def published(self, user):
        return self in Page.objects.published(user)
    published.boolean = True
    
    def get_meta_tags(self, language=None):
        if not language:
            language = translation.get_language()
        pagecontent_set = self.pagecontent_set.filter(is_published=True, language=language)
        tags = []
        tags += [MetaTag(page_content.keywords, 'keywords', lang=page_content.language) 
            for page_content in pagecontent_set.filter(is_published=True) if page_content.keywords]
        tags += [MetaTag(page_content.description, 'description', lang=page_content.language) 
            for page_content in pagecontent_set if page_content.description]
        tags += [MetaTag(page_content.page_topic, 'page_topic', lang=page_content.language) 
            for page_content in pagecontent_set if page_content.page_topic]
        return tags

class PageContent(models.Model):
    CONTENT_TYPES = (
        ('html', _('HTML')),
        ('markdown', _('Markdown')),
        ('textile', _('Textile')),
        ('rst', _('reStructuredText')),
        ('text', _('Plain text')),
    )
    page = models.ForeignKey(Page)
    language = models.CharField(max_length=2, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE[:2])
    is_published = models.BooleanField(default=True)
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPES, default=USE_TINYMCE and 'html' or 'text')
    allow_template_tags = models.BooleanField(default=True)

    created = models.DateTimeField(null=True, blank=True, default=datetime.datetime.now)
    modified = models.DateTimeField(null=True, blank=True, default=datetime.datetime.now)

    template = models.CharField(max_length=200, null=True, blank=True, help_text=_('Only specify this if you want to override the page template.'))

    position = models.CharField(max_length=32, null=True, blank=True, choices=[(pos[0], _(pos[1])) for pos in POSITIONS])

    title = models.CharField(max_length=200, null=True, blank=True, help_text=_('Used in navigation. Leave this empty to use the default title.'))
    slug = models.CharField(_('slug'), max_length=50, help_text=_('Only specify this if you want to give this page content a specific slug.'))
    page_title = models.CharField(max_length=250, null=True, blank=True, help_text=_('Used for page title. Should be no longer than 150 chars.'))
    keywords = TagField(_('keywords'), max_length=250, help_text=_('Comma separated'), null=True, blank=True)
    description = models.TextField(help_text=_('Keep between 150 and 1000 characters long.'), null=True, blank=True)
    page_topic = models.TextField(help_text=_('Keep between 150 and 1000 characters long.'), null=True, blank=True)
    content = models.TextField()

    def prepare(self):
        # Set the template and title for the page content, if they are not set (but don't save them)
        self.title = self.title or self.page.title
        self.template = self.template or self.page.template
        self.slug = self.slug or self.page.slug

        if not self.description:
            self.description = ''
        if not self.keywords:
            self.keywords = ''
        if not self.page_topic:
            self.page_topic = ''

        # Convert the content to HTML
        if self.content_type == 'html':
            pass # Nothing to do
        elif self.content_type == 'markdown':
            self.content = markdown(self.content)
        elif self.content_type == 'textile':
            self.content = textile(self.content)
        elif self.content_type == 'rst':
            self.content = rst(self.content)
        else:
            self.content = mark_safe(linebreaks(escape(self.content)))
        return self

    def save(self):
        self.modified = datetime.datetime.now()
        super(PageContent, self).save()

    def __unicode__(self):
        created = self.created and (', created: %s' % DateFormat(self.created).format('jS F Y H:i')) or ''
        modified = self.modified and (', modified: %s' % DateFormat(self.modified).format('jS F Y H:i')) or ''
        return u'%s (%s%s%s%s%s)' % (self.title or self.page.title, self.get_language_display(), created, modified, created and ', ' or '', self.is_published and _('published') or _('unpublished'))

    def language_bidi(self):
        return self.language in settings.LANGUAGES_BIDI 
