import os

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.db.models import permalink

from tinymce.util import SlugifyUniquely
import tinymce_global_settings as tinymce_settings

class Template(models.Model):
    title = models.CharField(_('title'), max_length=100)
    description = models.CharField(_('description'), max_length=200, blank=True)
    content = models.TextField(_('content'))
    name = models.CharField(_('name'), max_length=200, editable=False)
    is_snippet = models.BooleanField(_('is snippet'), default=True)
    
    class Meta:
        verbose_name = _('template')
        verbose_name_plural = _('templates')
        
    class Admin:
        list_display = ('__unicode__', 'get_name', 'is_snippet')
        list_filter = ('is_snippet',)
        js = (
            tinymce_settings.JS_SCRIPT_PATH,
            '/tinymce/init/tiny_mce_init.js?mode=textareas',
        )

    def __unicode__(self):
        return self.title
        
    def save(self):
        self.name = SlugifyUniquely(self, slug_base='title', slug_field='name')
        super(self.__class__, self).save()
    
    @permalink
    def get_absolute_url(self):
        return ('tinymce.views.get_template', [self.name])
    
    def get_name(self):
        return self.name
    
    def get_content(self):
        if self.is_snippet:
            return u'%s' % (self.content)
        else:
            return u'%s%s%s' % (u'<div class="mceTmpl">\n', self.content, u'\n</div>')
        
class CssClassManager(models.Manager):
    def render_css(self):
        return ''.join([u'%s .%s { %s }\n' % (css.element == 'all' and ' ' or css.element, css.css_class, css.css_style) for css in self.all()])

class CssClass(models.Model):
    ELEMENTS = (
        ('img', 'Image <img>'),
        ('a', 'Hyperlink <a>'),
        ('all', 'all Elements <*>'),
    )
    description = models.CharField(_('description'), max_length=200)
    element = models.CharField(choices=ELEMENTS, max_length=30, help_text=_('Determines for which elements this class can be used.'))
    css_class = models.CharField(_('CSS class'), max_length=30)
    css_style = models.TextField(_('CSS Style'), blank=True)
    
    objects = CssClassManager()
    
    class Admin:
        list_display = ('__unicode__', 'css_class', 'element')
        list_filter = ('element',)

    class Meta:
        verbose_name = _('CSS class')
        verbose_name_plural = _('CSS classes')

    def __unicode__(self):
        return self.description

    @permalink
    def get_absolute_url(self):
        return ('tinymce.views.get_css', [])

    def get_content(self):
        return u'%s%s%s' % ('<div class="mceTmpl">\n', self.content, '\n</div>')
        