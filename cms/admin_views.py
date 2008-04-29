from django.template import RequestContext, Context, loader
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.conf import settings
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django import newforms as forms

from cms import models
from cms import util
from cms import json
from cms import dynamicforms
from cms import views
from cms.cms_global_settings import *
from cms.forms import PageForm, PageContentForm, PAGE_FIELDS, PAGECONTENT_FIELDS

@staff_member_required
def page_add_edit(request, id=None):
    if id:
        page = get_object_or_404(models.Page, pk=id)
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
        if form.is_valid() and (add or pagecontent_forms.are_valid()):
            page = form.save()

            if not add:
                # Save the PageContents
                for pagecontent_form in pagecontent_forms:
                    try:
                        page_content = models.PageContent.objects.get(pk=pagecontent_form.id)
                    except models.PageContent.DoesNotExist:
                        page_content = models.PageContent() # Is this ok?
                    util.set_values(page_content, PAGECONTENT_FIELDS, pagecontent_form.cleaned_data)
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
            pagecontent_data = [PageContentForm(
                    initial=util.get_values(page_content, PAGECONTENT_FIELDS),
                    id=page_content.id
                ).render_js('from_template') for page_content in page_contents]


    return render_to_response('cms/page_add.html', {
        'title': u'%s %s' % (add and _('Add') or _('Edit'), _('page')),
            'page':page,
            'form':form,
            'add':add,
            'page_contents':page_contents,
            'page_addons': PAGE_ADDONS,
            'use_tinymce': unicode(USE_TINYMCE),
            'pagecontent_template':PageContentForm().render_js('from_template'),
            'pagecontent_data':pagecontent_data,
        'use_tinymce': USE_TINYMCE,
        }, context_instance=RequestContext(request))


@staff_member_required
def page_preview(request, id):
    form_id = request.POST.get('preview')
    try:
        pagecontent_form = [form for form in PageContentForm.get_forms(request) if form.postfix == form_id][0]
    except IndexError:
        raise Http404

    page = get_object_or_404(models.Page, pk=id)

    if pagecontent_form.is_valid():
        page_content = models.PageContent(page=page)
        util.set_values(page_content, PAGECONTENT_FIELDS, pagecontent_form.cleaned_data)
    else:
        return HttpResponse(_('<h2>Your form is not valid.</h2>')+smart_unicode(pagecontent_form.errors))

    return views.render_page(request, request.LANGUAGE_CODE, page, preview=page_content.prepare())

class NavigationForm(dynamicforms.Form):
    in_navigation = forms.BooleanField(required=False)
    is_published = forms.BooleanField(required=False)

@staff_member_required
def navigation(request):
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
        pages = dict([(page.id, page) for page in models.Page.objects.all()])
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

    hierarchy = models.Page.objects.hierarchy()

    try:
        rendered_navigation = render(hierarchy[0])
    except IndexError:
        rendered_navigation = _('<li>Please <a href="../page/add/">create a page</a> first.</li>')

    return render_to_response('cms/navigation.html', {
            'title': _('Edit pages'),
            'navigation': mark_safe('<ul id="navigation">%s</ul>' % rendered_navigation),
            'error': error,
        }, context_instance=RequestContext(request))

@staff_member_required
@json.view
def pagecontent_json(request, data):
    try:
        models.PageContent.objects.get(pk=data.get('id')).delete()
        return {}
    except models.PageContent.DoesNotExist:
        return { 'error': _('This page content has been already removed. Please reload the page and try again.') }



"""
def navigation_json(request):
    try:
        data = json.load(request.POST.get('json'))
        error = None
    except ValueError:
        error = _('Received invalid data.')
        data = None

    if data:
        try:
            models.Navigation.objects.get(pk=data.get('id')).delete()
        except models.Navigation.DoesNotExist:
            error = _('This page is not in this navigation. Please reload the page and try again.')

    data = { 'error': error }

    return HttpResponse(json.dump(data), mimetype='text/plain; charset=%s' % settings.DEFAULT_CHARSET)
"""
