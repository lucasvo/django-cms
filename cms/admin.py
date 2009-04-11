from django.contrib import admin
from django.template import RequestContext, Context, loader
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.admin.util import unquote
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django import forms

from cms.util import set_values, get_values
from cms.views import render_page
from cms.models import Page, PageContent
from cms.forms import PageForm, PageContentForm, NavigationForm, PAGECONTENT_FIELDS
from cms.decorators import json
from cms.conf.global_settings import PAGE_ADDONS, USE_TINYMCE

class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'created', 'modified', 'parent', 'position', 'in_navigation')
    list_filter = ('is_published',)
    search_fields = ('title', 'slug',)
    prepopulated_fields = {'title': ['slug',] }
    tinymce_js = (
        'admin/js/getElementsBySelector.js',
        'filebrowser/js/AddFileBrowser.js'
    )
    
    class Media:
        css = {
            "screen": ("cms/css/admin.css",)
        }
        js = (
            "cms/js/mootools.js",
            "cms/js/DateTimeShortcuts.js",
        )

    def __call__(self, request, url):
        # Delegate to the appropriate method, based on the URL.
        if url is None:
            # (r'^/$', 'admin_views.navigation'),
            return self.navigation(request)
        if url == "add":
            # (r'^add/$', 'admin_views.page_add_edit'),
            return self.page_add_edit(request)
        elif url == "content/json":
            # (r'^cms/pagecontent/json/$', 'admin_views.pagecontent_json'),
            return self.pagecontent_json(request)
        elif url.endswith('/preview'):
            # (r'^([0-9]+)/preview/$', 'admin_views.page_preview'),
            return self.page_preview(request, unquote(url[:-8]))
        elif url.endswith('/json'):
            # (r'^([0-9]+)/json/$', 'admin_views.page_add_edit'),
            return self.page_add_edit(request, unquote(url[:-5]))
        elif url.isdigit():
            # (r'^([0-9]+)/$', 'admin_views.page_add_edit'),
            return self.page_add_edit(request, unquote(url))
        else:
            return super(PageAdmin, self).__call__(request, url)

    def page_add_edit(self, request, id=None):
        model = self.model
        opts = model._meta

        if id:
            page = get_object_or_404(Page, pk=id)
            form = PageForm(request, instance=page)
            add = False
        else:
            page = None
            form = PageForm(request)
            add = True

        page_contents = not add and page.pagecontent_set.all()

        pagecontent_data = None

        if request.method == 'POST':
            if not add:
                pagecontent_forms = PageContentForm.get_forms(request)
                pagecontent_data = [pagecontent_form.render_js('from_template') for pagecontent_form in pagecontent_forms]


            if form.is_valid():
                page = form.save()

                if not add:
                    # Save the PageContents
                    for pagecontent_form in pagecontent_forms:
                        if pagecontent_form.id:
                            try:
                                page_content = PageContent.objects.get(pk=pagecontent_form.id)
                            except PageContent.DoesNotExist:
                                page_content = PageContent() # Is this ok?
                        else:
                            page_content = PageContent()
                        set_values(page_content, PAGECONTENT_FIELDS, pagecontent_form.cleaned_data)
                        page_content.page = page
                        page_content.save()

                # Inform the user
                if add:
                    request.user.message_set.create(message=_('The page was added successfully. Now you can create your content.'))
                else:
                    request.user.message_set.create(message=_('The page was updated successfully. You may edit it again below.'))

                return HttpResponseRedirect('../%d/' % page.id)

        else: # get
            if not add:
                pagecontent_data = []
                for page_content in page_contents:
                    content_form = PageContentForm(
                        initial=get_values(page_content, PAGECONTENT_FIELDS),
                        id=page_content.id)
                    pagecontent_data.append(content_form.render_js('from_template'))

        media = self.media
        if USE_TINYMCE:
            media.add_js(self.tinymce_js)
        media.add_js((
            "cms/js/dynamicforms.js",
            "cms/js/page_add.js",
        ))

        return render_to_response('cms/page_add.html', {
                'title': u'%s %s' % (add and _('Add') or _('Edit'), _('page')),
                'page': page,
                'form': form,
                'add':add,
                'page_contents': page_contents,
                'page_addons': PAGE_ADDONS,
                'pagecontent_template': PageContentForm().render_js('from_template'),
                'pagecontent_data': pagecontent_data,
                'use_tinymce': USE_TINYMCE,
                'root_path': self.admin_site.root_path,
                'media': mark_safe(media),
                'opts': opts,
            }, context_instance=RequestContext(request))

    def navigation(self, request):
        model = self.model
        opts = model._meta
        
        def render(obj):
            parent, children = obj
            template = loader.get_template('cms/navigation_item.html')
            content = template.render(Context({'page': parent}))
            return '<li id="navigation-%s">%s%s</li>' % (parent.id, content, children and '<ul>%s</ul>'%''.join([render(child) for child in children]) or '')

        def id(name):
            return int(name.split('-')[-1])

        def parents(pages, data, parent=None):
            pos = 1
            for d in data:
                page = pages[id(d['id'])]
                page.parent = parent
                page.position = pos
                pos += 1
                parents(pages, d['children'], page)

        error = None

        if request.method == 'POST':
            pages = dict([(page.id, page) for page in Page.objects.all()])
            for form in NavigationForm.get_forms(request):
                assert form.is_valid()
                try:
                    page = pages[int(form.id)]
                    page.in_navigation = form.cleaned_data['in_navigation']
                    page.is_published = form.cleaned_data['is_published']
                except KeyError:
                    pass # Should we fail silently?

            hierarchy_data = json.load(request.POST.get('navigation'))
            parents(pages, hierarchy_data)

            if len(hierarchy_data) == 1:
                [page.save() for page in pages.values()]
                request.user.message_set.create(message=_('The navigation was updated successfully. You may edit it again below.'))
                return HttpResponseRedirect('.')
            else:
                error = _('Your changes were discarded, because there must not be more than one root element. Make sure that there is only one root element.')

        hierarchy = Page.objects.hierarchy()

        try:
            rendered_navigation = render(hierarchy[0])
        except IndexError:
            rendered_navigation = _('<li>Please <a href="../page/add/">create a page</a> first.</li>')

        media = self.media
        media.add_js((
           "cms/js/nested.js",
           "cms/js/navigation.js",
        ))

        return render_to_response('cms/navigation.html', {
                'title': _('Edit pages'),
                'navigation': mark_safe('<ul id="navigation">%s</ul>' % rendered_navigation),
                'error': error,
                'media': mark_safe(media),
                'opts': opts,
                'root_path': self.admin_site.root_path,
            }, context_instance=RequestContext(request))

    def page_preview(self, request, id):
        form_id = request.POST.get('preview')
        try:
            pagecontent_form = [form for form in PageContentForm.get_forms(request) if form.postfix == form_id][0]
        except IndexError:
            raise Http404, _('Please fill in some page content.')

        page = get_object_or_404(Page, pk=id)

        if pagecontent_form.is_valid():
            page_content = PageContent(page=page)
            set_values(page_content, PAGECONTENT_FIELDS, pagecontent_form.cleaned_data)
        else:
            return HttpResponse(_('<h2>Your form is not valid.</h2>')+smart_unicode(pagecontent_form.errors))

        return render_page(request, request.LANGUAGE_CODE, page, preview=page_content.prepare())

    def pagecontent_json(self, request, data):
        try:
            PageContent.objects.get(pk=data.get('id')).delete()
            return {}
        except PageContent.DoesNotExist:
            return { 'error': _('This page content has been already removed. Please reload the page and try again.') }
    pagecontent_json = json.admin_view(pagecontent_json)

admin.site.register(Page, PageAdmin)
