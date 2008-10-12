from django import template
#from django.contrib.admin.templatetags.admin_modify import TabularBoundRelatedObject
#from django.contrib.admin.templatetags.admin_modify import StackedBoundRelatedObject
from django.template import loader
from django.conf import settings
from cms import cms_global_settings as cms_settings

register = template.Library()

def is_datetime(value):
    from django import newforms as forms
    return isinstance(value.field, forms.fields.DateTimeField)
is_datetime = register.filter(is_datetime)

def render_field(field):
    return {'field': field,}
render_field = register.inclusion_tag('cms/field.html')(render_field)
    
class EditInlineNode(template.Node):
    def __init__(self, rel_var):
        self.rel_var = template.Variable(rel_var)

    def render(self, context):
        from django.db import models
        relation = self.rel_var.resolve(context)
        add_on_name = u'%s.%s' % (relation.model.__module__, relation.model.__name__)
        if add_on_name in cms_settings.PAGE_ADDONS:
            context.push()
            """
            if relation.field.rel.edit_inline == models.TABULAR:
                bound_related_object_class = TabularBoundRelatedObject
            elif relation.field.rel.edit_inline == models.STACKED:
                bound_related_object_class = StackedBoundRelatedObject
            else:
                bound_related_object_class = relation.field.rel.edit_inline
            """
            original = context.get('original', None)
            bound_related_object = relation.bind(context['form'], original, bound_related_object_class)
            context['bound_related_object'] = bound_related_object
            t = loader.get_template(bound_related_object.template_name())
            output = t.render(context)
            context.pop()
            return output
        return ''

def edit_inline(parser, token):
    bits = token.contents.split()
    if len(bits) != 2:
        raise template.TemplateSyntaxError, "%s takes 1 argument" % bits[0]
    return EditInlineNode(bits[1])
cms_edit_inline = register.tag('cms_edit_inline', edit_inline)
