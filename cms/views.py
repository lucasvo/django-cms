import re

from django.db.models import Q
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext, Template, loader, TemplateDoesNotExist
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import translation
from django.utils.translation import ugettext as _
from django.contrib.sites.models import Site, RequestSite
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.http import urlquote

from cms.forms import SearchForm
from cms.models import Page
from cms.managers import RootPageDoesNotExist
from cms.util import PositionDict, language_list, resolve_dotted_path
from cms.conf.global_settings import SITE_TITLE, TEMPLATETAGS, POSITIONS, \
                                     DEFAULT_TEMPLATE, LANGUAGE_DEFAULT, \
                                     DISPLAY_ROOT, LANGUAGE_REDIRECT, \
                                     REQUIRE_LOGIN

def get_page_context(request, language, page, extra_context={}):
    context = RequestContext(request)
    path = list(page.get_path())

    try:
        page_number = int(request.GET.get('page'))
    except (TypeError, ValueError):
        page_number = 1

    context.update({
        'page': page,
        'page_number': page_number,
        'path': path,
        'language': language,
        'root':'/%s/' % language,
        'site_title': SITE_TITLE,
    })
    context.update(extra_context)
    return context

def render_pagecontent(page_content, context):
    # Parse template tags
    if page_content.allow_template_tags:
        template = Template(
                '{%% load i18n cms_base cms_extras %s %%}'
                '{%% cms_pagination %d %%}%s{%% cms_end_pagination %%}' % (
                    ' '.join(TEMPLATETAGS),
                    context['page_number'],
                    page_content.content
                )
            )
        content = template.render(context)
    else:
        content = page_content.content

    return page_content.title, content


def render_page(request, language, page, template_name=None, preview=None, 
        args=None, login_url=settings.LOGIN_URL, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Renders a page in the given language.

    A template_name can be given to override the default page template.
    A PageContent object can be passed as a preview.
    """
    # if there is no published root page
    if not Page.on_site.root().published(request.user) or not page.published(request.user):
        raise Http404

    # if the given page requires login but the user is not authenticated
    if page.requires_login and not request.user.is_authenticated():
        path = urlquote(request.get_full_path())
        redirect_args = login_url, redirect_field_name, path
        return HttpResponseRedirect('%s?%s=%s' % redirect_args)

    # Make translations using Django's i18n work
    translation.activate(language)
    request.LANGUAGE_CODE = translation.get_language()

    # Initialize content/title dicts.
    content_dict = PositionDict(POSITIONS[0][0])
    title_dict = PositionDict(POSITIONS[0][0])

    # Initialize default context.
    context = get_page_context(request, language, page)

    # Call a custom context function for this page, if it exists.
    if page.context:
        try:
            func = resolve_dotted_path(page.context)
        except (ImportError, AttributeError, ValueError), e:
            raise StandardError, 'The context function for this page does not exist. %s: %s' % (e.__class__.__name__, e)
        if args:
            response = func(request, context, args)
        else:
            response = func(request, context)
        if response:
            return response

    for n, position in enumerate(POSITIONS):
        position = position[0]

        if preview and position == preview.position:
            page_content = preview
        else:
            page_content = page.get_content(language, position=position)

        print page_content
        for content in page_content:
            if n == 0:
                # This is the main page content.
                context.update({
                    'page_content': content,
                    'page_title': content.page_title or content.title,
                })
            title_dict[position], content_dict[position] = render_pagecontent(page_content, context)

    context.update({
        'content': content_dict,
        'title': title_dict,
    })

    # Third processing stage: Use the specified template
    # Templates are chosen in the following order:
    # 1. template defined in page (over `page_content.prepare()`)
    # 2. template defined in function arg "template_name"
    # 3. template defined in settings.DEFAULT_TEMPLATE
    # If preview, then _preview is appended to the templates name. If there's no preview template: fallback to the normal one
    if template_name:
        template_path = template_name
    elif page.template:
        template_path = page.template
    else:
        template_path = DEFAULT_TEMPLATE

    if preview: # append _preview to template name
        if template_path.endswith('.html'):
            template_path_preview = template_path[:template_path.rfind('.html')] + '_preview.html'
        else:
            template_path_preview += '_preview'
        try:
            template = loader.get_template(template_path_preview)
        except TemplateDoesNotExist:
            template = loader.get_template(template_path)
    else:
        try:
            template = loader.get_template(template_path)
        except TemplateDoesNotExist:
            if settings.DEBUG:
                raise
            else:
                template = loader.get_template(DEFAULT_TEMPLATE)

    return HttpResponse(template.render(context))


def handle_page(request, language, url):
    # TODO: Objects with overridden URLs have two URLs now. This shouldn't be the case.

    # First take a look if there's a navigation object with an overridden URL
    pages = Page.on_site.overridden(url=url)
    if pages:
        return render_page(request, language, pages[0])

    # If not, go and look it up
    parts = url and url.split('/') or []

    root = Page.on_site.root()

    if not parts and not DISPLAY_ROOT:
        try:
            return HttpResponseRedirect(Page.on_site.filter(parent=root)[0].get_absolute_url(language))
        except IndexError:
            raise RootPageDoesNotExist, unicode(_('Please create at least one subpage or enable DISPLAY_ROOT.'))

    parent = root
    pages = None
    args = []

    for part in parts:
        pages = parent.page_set.filter(
            Q(slug=part) |
            Q(pagecontent__slug=part)
        ) or parent.page_set.filter(slug='*')
        if not pages:
            raise Http404
        parent = pages[0]
        if parent.slug == '*':
            args.append(part)

    if pages:
        page = pages[0]
    else:
        page = root

    if page.redirect_to:
        return HttpResponseRedirect(page.redirect_to.get_absolute_url(language))

    return render_page(request, language, page, args)


def handler(request):
    """
    Main handler view that calls the views to render a page or redirects to
    the appropriate language URL.
    """
    url = request.path

    languages = language_list()
    language = None

    # Skip multiple slashes in the URL
    if '//' in url:
        url = re.sub("/+" , "/", url)
        return HttpResponseRedirect('%s' % url)

    try:
        language = request.LANGUAGE_CODE
    except AttributeError:
        raise StandardError, "Please add django.middleware.locale.LocaleMiddleware to your MIDDLEWARE_CLASSES."

    # This shouldn't happen
    if not language in languages:
        language = settings.LANGUAGE_CODE
    if not language in languages:
        language = LANGUAGE_DEFAULT
    if not language in languages:
        raise Exception, _("Please define LANGUAGES in your project's settings.")

    # Determine the language and redirect the user, if required
    if LANGUAGE_REDIRECT:
        if url:
            for l in languages:
                if url.startswith('/%s/' % l):
                    return handle_page(request, l, url[len(l)+2:-1])

        # Make sure the language code is prepended to the URL
        # See also: http://www.mail-archive.com/django-users@googlegroups.com/msg11604.html
        if not DISPLAY_ROOT and url == '/':
            # Avoid two redirects: handle_page will return a redirect to the correct page.
            return handle_page(request, language, '')
        return HttpResponseRedirect('/%s%s' % (language, url))
            
    else:
        # TODO: Not implemented
        pass

    return handle_page(request, language, url[1:-1])

def search(request, form_class=SearchForm, extra_context={}, 
        template_name="cms/search.html"):
    """
    Performs a search over Page and PageContent fields depending on the
    current language and also returns the search results for other languages.
    """

    language = request.LANGUAGE_CODE[:2]
    page = Page.on_site.root()
    context = get_page_context(request, language, page)

    if request.GET.get('query', False):
        # create search form with GET variables if given
        search_form = form_class(request.GET)

        if search_form.is_valid():
            query = search_form.cleaned_data['query']

            # perform actual search
            search_results = Page.on_site.search(request.user, query, language)
            page_ids = [res['id'] for res in search_results.values('id')]
            search_results_ml = Page.on_site.search(request.user, query).exclude(id__in=page_ids)

            # update context to contain query and search results
            context.update({
                'search_results': search_results,
                'search_results_ml': search_results_ml,
                'query': query,
            })
    else:
        search_form = form_class()

    context.update({
        'search_form': search_form,
    })
    return render_to_response(template_name, extra_context,
        context_instance=RequestContext(request, context))

if REQUIRE_LOGIN:
    handler = staff_member_required(handler)
    search = staff_member_required(search)
