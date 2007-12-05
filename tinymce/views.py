from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from tinymce import models
import tinymce_settings

def get_css(request):
    return HttpResponse(models.CssClass.objects.render_css())

def init_mce(request):
    context = RequestContext(request)
    if request.method == 'GET':
        context.update({
            'mode': request.GET.get('mode', tinymce_settings.MODE),
            'elements': request.GET.get('elements', ''),                        
            'theme': request.GET.get('theme', 'advanced'),
            'plugins': request.GET.get('plugins', 'advimage,advlink,table,searchreplace,contextmenu,fullscreen,template,autosave,noneditable'),
            'language': request.GET.get('language', request.LANGUAGE_CODE[0:2]),
            'theme': request.GET.get('theme', 'advanced'),
            'width': request.GET.get('width', tinymce_settings.TINYMCE_WIDTH),
            'height': request.GET.get('height', '480'),
            'content_css': request.GET.get('content_css', tinymce_settings.CONTENT_CSS),
            'editor_css': request.GET.get('editor_css', ''),
            'popup_css': request.GET.get('popup_css', ''),
            'templates': models.Template.objects.all(),
            'advimage_styles': models.CssClass.objects.filter(element='img'),
            'advlink_styles': models.CssClass.objects.filter(element='a'),
            'extended_valid_elements': tinymce_settings.__dict__.get('EXTENDED_VALID_ELEMENTS', 'a[class|name|href|title|onclick|target],img[class|src|alt=image|title|onmouseover|onmouseout|name],hr[class],span[class|style]'),
            'forced_root_block': tinymce_settings.__dict__.get('FORCED_ROOT_BLOCK', ''),
            # additional context
            'ADMIN_MEDIA_URL' : settings.ADMIN_MEDIA_PREFIX,
        })

        if 'filebrowser' in settings.INSTALLED_APPS:
            context.update({'file_browser': True})
            
    return render_to_response('tinymce/tiny_mce_init.js', context, context_instance=RequestContext(request))

def get_template(request, url):
    templ = get_object_or_404(models.Template, name=url)
    return HttpResponse(templ.get_content())