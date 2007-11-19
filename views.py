import re

from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext, Template, loader
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import html, translation
from django.utils.translation import gettext as _
from django.utils.safestring import mark_safe

from cms import models
from cms.cms_global_settings import *
from cms.util import language_list

import markdown


def render_pagecontent(request, language, page, page_content, args=None):
    path = list(page.get_path())

    try:
        page_number = int(request.GET.get('page'))
    except (TypeError, ValueError):
        page_number = 1

    context = RequestContext(request)
    context.update({
            'page':page,
            'page_content':page_content,
            'page_number':page_number,
            'path':path,
            'language':language,
            'root':'/%s/'%language,
            'site_title':SITE_TITLE,
            'title':page_content.title,
        })

    if page.context:
        try:
            dot = page.context.rindex('.')
            mod_name, func_name = page.context[:dot], page.context[dot+1:]
            func = getattr(__import__(mod_name, {}, {}, ['']), func_name)
        except (ImportError, AttributeError, ValueError), e:
            raise StandardError, 'The context function for this page does not exist. %s: %s' % (e.__class__.__name__, e)
        if args:
            response = func(request, context, args)
        else:
            response = func(request, context)
        if response:
            return response

    # First processing stage: Parse template tags
    if page_content.allow_template_tags:
        template = Template('{%% load i18n cms_base cms_extras %s %%}{%% cms_pagination %d %%}%s{%% cms_end_pagination %%}' % (
                ' '.join(TEMPLATETAGS),
                page_number,
                page_content.content
            ))
        content = template.render(context)
    else:
        content = page_content.content

    # Second processing stage: Convert the content to HTML
    if page_content.content_type == 'html':
        pass # Nothing to do
    elif page_content.content_type == 'markdown':
        content = markdown.markdown(content)
    else:
        content = html.linebreaks(html.escape(content))

    # Third processing stage: Use the specified template
    context.update({ 'content': mark_safe(content) })

    template = loader.get_template(page_content.template or DEFAULT_TEMPLATE)

    return HttpResponse(template.render(context))


def render_page(request, language, page, args=None):
    if not page.is_published:
        raise Http404

    # Make translations using Django's i18n work
    translation.activate(language)
    request.LANGUAG_CODE = translation.get_language()

    page_content = page.get_content(language)

    return render_pagecontent(request, language, page, page_content, args)


def handle_page(request, language, url):

    # TODO: Objects with overriden URLs have two URLs now. This shouldn't be the case.

    # First take a look if there's a navigation object with an overriden URL
    pages = models.Page.objects.filter(override_url=True, overriden_url=url)
    if pages:
        return render_page(request, language, pages[0])

    # If not, go and look it up
    #parts = url and ('/%s'%url).split('/') or ['']
    parts = url and url.split('/') or []

    root = models.Page.objects.root()

    if not parts and not DISPLAY_ROOT:
        return HttpResponseRedirect(models.Page.objects.filter(parent=root)[0].get_absolute_url())

    parent = root

    pages = None

    args = []

    for part in parts:
        pages = parent.page_set.filter(slug=part) or parent.page_set.filter(slug='*')
        if not pages:
            raise Http404
        parent = pages[0]
        if parent.slug == '*':
            args.append(part)

    if pages:
        page = pages[0]
    else:
        page = models.Page.objects.root()

    return render_page(request, language, page, args)


def handler(request, url=''):
    languages = language_list()
    language = None

    # Skip multiple slashes in the URL
    do_redirect = False
    if '//' in url:
        url = re.sub("/+" , "/", url)
        do_redirect = True
    if url and url[0] == '/':
        url = url[1:]
        do_redirect = True
    if url and url[-1] == '/':
        url = url[:-1]
        do_redirect = True
    if do_redirect:
        return HttpResponseRedirect('/%s/'%url)

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
                if url == l:
                    return handle_page(request, l, '')
                if url.startswith('%s/'%l):
                    return handle_page(request, l, url[len(l)+1:])

        # Make sure the language code is prepended to the URL
        # See also: http://www.mail-archive.com/django-users@googlegroups.com/msg11604.html
        return HttpResponseRedirect('/%s/%s' % (language, url))
            
    else:
        # TODO: Not implemented
        pass

    return handle_page(request, language, url)

if REQUIRE_LOGIN:
    handler = staff_member_required(handler)
