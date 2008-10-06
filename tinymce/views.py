from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from tinymce import models
import tinymce_global_settings as tinymce_settings

def get_css(request):
    return HttpResponse(models.CssClass.objects.render_css())

def get_conf_var(name, default='', request=None, config=None):
    try:
        # if request given:
            # 1st: look if GET knows something
            # 2nd: look in the settings (for the config given in the request or default if no config given)
            # 3rd: take the default
        # if request == None:
            # 1st: look in the settings
            # 2nd: take the default
        # If you don't want to let someone hijack a setting (over GET), don't pass a request object
        if request:
            if not config:
                config = request.GET.get("tm_config", "default") 
            ret = request.GET.get(name, tinymce_settings.__dict__.get(config).get(name.upper())) or default
            return ret 
        else:
            if not config:
                config = "default" 
            return tinymce_settings.__dict__.get(config).get(name.upper()) or request.GET.get(name, default)
    except AttributeError:
        return default

def init_mce(request):
    context = RequestContext(request)
    if request.method == 'GET':
        config = request.GET.get("tm_config", "default") 
        context.update({
            'mode': get_conf_var('mode', request=request),
            'elements': get_conf_var('elements', request=request),                        
            'theme': get_conf_var('theme', 'advanced', config=config),
            'theme_advanced_buttons1': get_conf_var('theme_advanced_buttons1', config=config),
            'theme_advanced_buttons2': get_conf_var('theme_advanced_buttons2', config=config),
            'theme_advanced_buttons3': get_conf_var('theme_advanced_buttons3', config=config),
            'theme_advanced_blockformats': get_conf_var('theme_advanced_blockformats', default="p,h2,h3,h4", config=config),
            'plugins': get_conf_var('plugins', config=config),
            'language': get_conf_var('language', request.LANGUAGE_CODE[:2], request=request),
            'theme': get_conf_var('theme', 'advanced', config=config),
            'width': get_conf_var('width', 520, config=config),
            'height': get_conf_var('height', 480, config=config),
            'content_css': get_conf_var('content_css', request=request),
            'editor_css': get_conf_var('editor_css', request=request),
            'popup_css': get_conf_var('popup_css', '', config=config),
            'templates': models.Template.objects.all(),
            'advimage_styles': models.CssClass.objects.filter(element='img'),
            'advlink_styles': models.CssClass.objects.filter(element='a'),
            'theme_advanced_styles': models.CssClass.objects.filter(element='all'),
            'extended_valid_elements': get_conf_var('extended_valid_elements', config=config),
            'invalid_elements': get_conf_var('invalid_elements', config=config),
            'forced_root_block': get_conf_var('forced_root_block', '', config=config),
            'show_styles_menu': get_conf_var('show_styles_menu', request=request),
            'theme_advanced_resizing': get_conf_var('theme_advanced_resizing', request=request),
            'theme_advanced_path':  get_conf_var('theme_advanced_path', request=request),
            # additional context
            'ADMIN_MEDIA_URL' : settings.ADMIN_MEDIA_PREFIX,
        })
        if context['show_styles_menu'] and context['theme_advanced_styles']:
            context.update({'theme_advanced_buttons2_add': 'styleselect,removeformat'})
        
        if 'filebrowser' in settings.INSTALLED_APPS:
            context.update({'file_browser': True})
            
    return render_to_response('tinymce/tiny_mce_init.js', context, context_instance=RequestContext(request))

def get_template(request, url):
    if url[-1] == '/':
        url = url[:-1]
    templ = get_object_or_404(models.Template, name=url)
    return HttpResponse(templ.get_content())

def get_cmspages_link_list(request):
    try:
        from cms.models import Page
        return HttpResponse(u'var tinyMCELinkList = new Array(%s);' % u', '.join([u'["%s", "%s"]' % (page.get_path(), page.get_absolute_url()) for page in Page.objects.all()]))
    except ImportError:
        return HttpResponse('var tinyMCELinkList = new Array();')
    