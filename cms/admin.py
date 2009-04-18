# -*- coding: utf-8 -*-
from django.contrib import admin
from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.http import HttpResponseRedirect
from django import forms
from django.template import RequestContext, Context, loader
from django.core import serializers

import simplejson as json

from cms.models import Page, PageTranslation
from cms.forms import PageForm, PageTranslationForm


class PageAdmin(admin.ModelAdmin):
    
    class Media:
        css = {
            "screen": ("cms/css/admin.css",)
        }
        js = (
        
            "cms/js/jquery-1.3.2.min.js",
            "cms/js/jquery-ui-1.7.1.custom.min.js",
            "cms/js/admin.js",
         )
        
 
    def get_urls(self):
        urls = super(PageAdmin, self).get_urls()
        page_urls = patterns('',
            url(r'^$', self.admin_site.admin_view(self.page_tree), name='admin_cms_page_tree'),
            url(r'^([0-9]+)/$', self.admin_site.admin_view(self.page_add_edit)),
        )
        return page_urls + urls

    def page_add_edit(self, request, page_id=None):
        model = self.model
        opts = model._meta
        media = self.media
        media.add_css({
            'all':(settings.ADMIN_MEDIA_PREFIX+'css/forms.css',)
            })                  
        
        if page_id:
            page = get_object_or_404(Page, pk=page_id)
            page_form = PageForm(request.method == 'POST' and request.POST or None, instance=page)
            add = False
            page_translation_forms = []
            for language in settings.LANGUAGES:
                p_t = PageTranslation.objects.filter(language=language[0], model=page)
                if len(p_t) == 1:
                    p_t_form = PageTranslationForm(prefix=language[0], instance=p_t)
                else:
                    p_t_form = PageTranslationForm(prefix=language[0])
                page_translation_forms.append((language, p_t_form))

        else:
            page_form = PageForm(request.method == 'POST' and request.POST or None)
            page = None
            add = True 

        if request.method == 'POST':
            print request.POST
            #if form.is_valid():
            #    album = form.save()
            #    return HttpResponseRedirect('../%d/' % page.id)
                        
        return direct_to_template(request, 'admin/cms/page_add_edit.html', {
                'title':(add and _('Add %s') % _('page') or _('Edit %s') % _('page')),
                'page':page,
                'add': add,
                'page_form':page_form,
                'page_translation_forms':page_translation_forms,
                'languages':settings.LANGUAGES,                
                'root_path':self.admin_site.root_path,
                'opts':opts,
                'media':mark_safe(media)
                #'sessionid':request.COOKIES[settings.SESSION_COOKIE_NAME],
            })

    def page_tree(self, request):
        model = self.model
        opts = model._meta

        media = self.media
        media.add_js((
            "cms/js/jTree/jquery.jtree.1.0.js",
            "cms/js/jsonStringify.js",
        ))

        pages = Page.objects.all()
        
        def render(obj):
            parent, children = obj
            template = loader.get_template('admin/cms/tree_item.html')
            content = template.render(Context({'page': parent}))
            return u'<li id="navigation-%s">%s%s</li>' % (parent.id, content, children and u'<ul>%s</ul>'%''.join([render(child) for child in children]) or '')

        error = None

        def reorder_tree(parent, elements):
            last_pc = None
            for el in elements:
                pc = Page.objects.get(pk=el['object']['id'][11:])
                if last_pc:
                    pc.move_to(last_pc, 'right')
                else:
                    pc.move_to(parent, 'first-child')
                pc.save()
                if el.has_key('children'):
                    reorder_tree(pc, el['children'])
                last_pc = pc

        if request.method == 'POST':
            hierarchy_data = json.loads(request.POST.get('json'))
            for el in hierarchy_data:
                p = Page.objects.get(pk=el['object']['id'][11:])
                p.move_to(None)
                p.save()
                if el.has_key('children'):
                    reorder_tree(p, el['children'])
                    
        hierarchy = Page.objects.hierarchy()
        rendered_navigation = u''
        for element in hierarchy:
            try:
                rendered_navigation += render(element)
            except IndexError:
                rendered_navigation = _('<li>Please <a href="../page/add/">create a page</a> first.</li>')
            
        return direct_to_template(request, 'admin/cms/page_tree.html', {
                'title': _('Edit pages'),
                'opts': opts,
                'media': mark_safe(media),
                'navigation':mark_safe('<ul id="navigation" class="navigation">%s</ul>' % rendered_navigation),
                'pages': pages,
                'root_path': self.admin_site.root_path,
            })

admin.site.register(Page, PageAdmin)
admin.site.register(PageTranslation)
