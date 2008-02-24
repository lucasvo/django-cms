from django import template
from django.conf import settings
from django.utils.html import escape

from cms import models
from cms.cms_global_settings import *
from cms import languages


register = template.Library()

# TODO: There's some redundancy here
# TODO: {% cms_title nav %}


class CmsSubpagesNode(template.Node):
    def __init__(self, nav, varname):
        self.nav = nav
        self.varname = varname

    def render(self, context):
        nav = template.resolve_variable(self.nav, context)
        try:
            if not isinstance(nav, models.Page):
                page = models.Page.objects.get(pk=nav)
            else:
                page = nav
        except models.Page.DoesNotExist:
            context[self.varname] = None
        else:
            pages = models.Page.objects.filter(parent=page)
            context[self.varname] = pages
        return ''

@register.tag
def cms_subpages(parser, token):
    tokens = token.contents.split()
    if len(tokens) != 4:
        raise template.TemplateSyntaxError, "'%s' tag requires three arguments" % tokens[0]
    if tokens[2] != 'as':
        raise template.TemplateSyntaxError, "Second argument to '%s' tag must be 'as'" % tokens[0]
    return CmsSubpagesNode(tokens[1], tokens[3])


class CmsNavigationNode(template.Node):
    def __init__(self, level, varname):
        self.level = int(level)
        self.varname = varname

    def render(self, context):
        try:
            path = template.resolve_variable('path', context)
        except template.VariableDoesNotExist:
            return ''
        if self.level >= 0 and self.level <= len(path):
            pages = models.Page.objects.filter(in_navigation=True)
            if self.level == 0:
                pages = pages.filter(parent__isnull=True)
            else:
                pages = pages.filter(parent=path[self.level-1])
            context[self.varname] = pages
        else:
            context[self.varname] = None
        return ''

@register.tag
def cms_navigation_level(parser, token):
    tokens = token.contents.split()
    if len(tokens) != 4:
        raise template.TemplateSyntaxError, "'%s' tag requires three arguments" % tokens[0]
    if tokens[2] != 'as':
        raise template.TemplateSyntaxError, "Second argument to '%s' tag must be 'as'" % tokens[0]
    return CmsNavigationNode(tokens[1], tokens[3])


class CmsPagecontentNode(template.Node):
    def __init__(self, item, varname):
        self.item = item
        self.varname = varname

    def render(self, context):
        page = template.resolve_variable(self.item, context)
        context[self.varname] = page.get_content(context['language'])
        return ''

@register.tag
def cms_pagecontent(parser, token):
    tokens = token.contents.split()
    if len(tokens) != 4:
        raise template.TemplateSyntaxError, "'%s' tag requires three arguments" % tokens[0]
    if tokens[2] != 'as':
        raise template.TemplateSyntaxError, "Second argument to '%s' tag must be 'as'" % tokens[0]
    return CmsPagecontentNode(tokens[1], tokens[3])


class CmsLanguageLinksNode(template.Node):
    def render(self, context):
        url = context['page'].get_absolute_url()
        return ' '.join(['<a href="/%s/%s">%s</a>' % (code, url, languages.VERSION.get(code, name)) for code, name in context['LANGUAGES'] if code != context['language']])

@register.tag
def cms_language_links(parser, token):
    return CmsLanguageLinksNode()


class CmsLinkNode(template.Node):
    def __init__(self, name, html=False):
        self.name = name
        self.html = html

    def render(self, context):
        name = template.resolve_variable(self.name, context)
        if isinstance(name, int):
            try:
                page = models.Page.objects.get(pk=name)
            except models.Page.DoesNotExist:
                return self.html and '<a href="#">(none)</a>' or '#'
        else:
            page = name

        link = page.get_link(context['language'])

        if self.html:
            page_content = page.get_content(context.get('language'))
 
            extra_class = ''
            try:
                active_page = template.resolve_variable('page', context)

                if active_page == page:
                    extra_class = ' class="active"'
                elif page in active_page.get_path():
                    extra_class = ' class="active_path"'
            except template.VariableDoesNotExist:
                pass

            return '<a%s href="%s">%s</a>' % (extra_class, link, escape(page_content and page_content.title or page.title))
        else:
            return link


@register.tag
def cms_link(parser, token):
    tokens = token.split_contents()
    return CmsLinkNode(tokens[1])

@register.tag
def cms_html_link(parser, token):
    tokens = token.split_contents()
    return CmsLinkNode(tokens[1], True)


class CmsIsSubpageNode(template.Node):
    def __init__(self, sub_page, page, nodelist):
        self.sub_page = sub_page 
        self.page = page
        self.nodelist = nodelist

    def render(self, context):
        sub_page = template.resolve_variable(self.sub_page, context)
        page = template.resolve_variable(self.page, context)

        if isinstance(page, int):
            page = models.Page.objects.get(pk=page)
        if isinstance(sub_page, int):
            sub_page = models.Page.objects.get(pk=sub_page)

        while sub_page:
            if sub_page == page:
                return self.nodelist.render(context)
            sub_page = sub_page.parent

        return ''

@register.tag
def if_cms_is_subpage(parser, token):
    tokens = token.contents.split()
    if len(tokens) != 3:
        raise template.TemplateSyntaxError, "'%s' tag requires two arguments" % tokens[0]
    nodelist = parser.parse(('end_if_cms_is_subpage',))
    parser.delete_first_token()
    return CmsIsSubpageNode(tokens[1], tokens[2], nodelist)

@register.filter(name='cms_yesno')
def yesno(value):
    if value == '':
        return '<img src="%simg/admin/icon-unknown.gif" alt="%s" />' % (settings.MEDIA_URL, _('Unknown'))
    elif value:
        return '<img src="%simg/admin/icon-yes.gif" alt="%s" />' % (settings.MEDIA_URL, _('Yes'))
    else:
        return '<img src="%simg/admin/icon-no.gif" alt="%s" />' % (settings.MEDIA_URL, _('No'))

@register.filter(name='cms_get_content_title')
def get_content_title(page, language):
    return page.get_content(language).title


class CmsPaginationNode(template.Node):
    def __init__(self, nodelist, num_pages):
        self.nodelist = nodelist
        self.num_pages = num_pages

    def render(self, context):
        context['number_of_pages'] = self.num_pages
        context['page_numbers'] = range(1, self.num_pages+1)
        context['more_than_one_page'] = self.num_pages>1
        return self.nodelist.render(context)

@register.tag
def cms_pagination(parser, token):
    tokens = token.contents.split()
    if len(tokens) != 2:
        raise template.TemplateSyntaxError, "'%s' tag requires one argument" % tokens[0]

    page = int(tokens[1])

    if page < 1:
        page = 1

    num_pages = 1
    the_nodelist = None

    while True:
        nodelist = parser.parse(('cms_new_page','cms_end_pagination'))
        if num_pages == page:
            the_nodelist = nodelist
        token_name = parser.next_token().contents
        #parser.delete_first_token()
        if token_name == 'cms_end_pagination':
            if not the_nodelist:
                # Display the last page if the page number is too big
                the_nodelist = nodelist 
            break
        num_pages += 1

    return CmsPaginationNode(the_nodelist, num_pages)
