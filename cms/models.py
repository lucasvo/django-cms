import datetime

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from cms.managers import PageManager

#from cms.conf.global_settings import LANGUAGE_REDIRECT, USE_TINYMCE, POSITIONS
POSITIONS = []

from multiling import MultilingualModel

import mptt

class Position(models.Model):
    name = models.CharField(max_length=30)
    slug = models.CharField(_('Slug used in the template'), max_length=30)
    description = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return self.name

class Template(models.Model):
    name = models.CharField(max_length=30)
    template = models.CharField(max_length=100, 
        help_text=_('Path to the template, relative to the project root'))
    description = models.TextField(null=True, blank=True)
    positions = models.ManyToManyField(Position, blank=True, related_name='positions')
    default_position = models.ForeignKey(Position, null=True, blank=True, related_name='default_position')
    # TODO: Check if default position is also in positions
    
    def __unicode__(self):
        return self.name

class PageTranslation(models.Model):
    model = models.ForeignKey('Page')
    language = models.CharField(max_length=5, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE[:2])

    menu_title = models.CharField(_('menu title'), max_length=200, help_text=_('The title displayed in the menu.'))
    slug = models.SlugField(_('slug'), help_text=_('The name of the page that appears in the URL. A slug can contain letters, numbers, underscores or hyphens.'))

    page_title = models.CharField(_('page title'), max_length=200, null=True, blank=True, 
        help_text=_('The title of the page. This title should quickly summarize the content. It will be used in the title tag and is important for SEO.'))
    keywords = models.CharField(_('keywords'), max_length=250, 
        help_text=_('Between 10 and 30 words, comma separated'), null=True, blank=True)
    description = models.TextField(help_text=_('Keep between 150 and 1000 characters long.'), null=True, blank=True)

    def __unicode__(self):
        return self.menu_title


class Page(MultilingualModel):
    created = models.DateTimeField(null=True, blank=True, default=datetime.datetime.now)
    modified = models.DateTimeField(null=True, blank=True, default=datetime.datetime.now)

    in_navigation = models.BooleanField(_('display in navigation'), default=True)

    is_published = models.BooleanField(_('is published'), default=True, 
        help_text=_('Whether or not the page is accessible from the web.'))
    publish_start = models.DateTimeField(_('start publishing'), null=True, blank=True)
    publish_end = models.DateTimeField(_('finish publishing'), null=True, blank=True)

    requires_login = models.BooleanField(_('requires login'), 
        help_text=_('If checked, only logged-in users can view the page. Automatically enabled if the parent page requires a login.'))

    redirect_to = models.ForeignKey('self', null=True, blank=True, related_name='redirected_pages')

    context = models.CharField(max_length=200, null=True, blank=True, 
        help_text=_('Dotted path to a python function that receives two arguments (request, context) and can update the context.'))

    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')

    template = models.ForeignKey(Template, null=True, blank=True)
    
    def __unicode__(self):
        if self.get_translated_or_none('menu_title'):
            return self.get_translated_or_none('menu_title')
        else:
            return 'Page object'

    class Meta:
        translation = PageTranslation
        multilingual = ['page_title', 'menu_title', 'slug', 'keywords', 'description']

    objects = PageManager()

mptt.register(Page)



class PageContent(models.Model):
    '''BaseClass for the content on a page.'''

    page = models.ForeignKey(Page)
    
    content_type = models.ForeignKey(ContentType)
    
    language = models.CharField(max_length=5, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE[:2])

    is_published = models.BooleanField(_('is published'), default=True, help_text=_('Whether or not the page is accessible from the web.'))
    publish_start = models.DateTimeField(_('start publishing'), null=True, blank=True)
    publish_end = models.DateTimeField(_('finish publishing'), null=True, blank=True)

    created = models.DateTimeField(null=True, blank=True, default=datetime.datetime.now)
    modified = models.DateTimeField(null=True, blank=True, default=datetime.datetime.now)

    position = models.ForeignKey(Position, null=True)

class HTMLPageContent(PageContent):
    '''This is an HTML PageContent that will display static HTML. It may contain template tags''' 
    
    content = models.TextField(null=True, blank=True)
    allow_template_tags = models.BooleanField(blank=True)
    
    def save(self):
        self.content_type = ContentType.objects.get_for_model(self.__class__)
        super(HTMLPageContent, self).save()
