from django.conf import settings
from django.utils.safestring import mark_safe
from django.template.defaultfilters import force_escape

class MetaTag:
    """Simple class to output XHTML conform <meta> tags."""
    def __init__(self, content='', name=None, http_equiv=None, scheme=None, lang=None):
        self.content = content
        self.name = name
        self.http_equiv = http_equiv
        self.scheme = scheme
        self.lang = lang and lang.lower()[:5]
        
    def __unicode__(self, request=None):
        if not self.lang:
            if not request:
                lang = settings.LANGUAGE_CODE[:2]
            else:
                lang = request.LANGUAGE_CODE[:2]
        else:
            lang = self.lang
        attrs = u''
        if self.name:
            attrs += u'name="%s" ' % force_escape(self.name)
        attrs += u'content="%s" ' % force_escape(self.content)
        if self.http_equiv:
            attrs += u'http_equiv="%s" ' % force_escape(self.http_equiv)
        if self.scheme:
            attrs += u'scheme="%s" ' % force_escape(self.scheme)
        attrs += u'lang="%s" ' % force_escape(lang)
        return mark_safe(u'<meta %s/>' % attrs)

def to_utf8(string):
    if isinstance(string, str):
        return unicode(string, 'utf8')
    else:
        return string
    
def from_utf8(string):
    if isinstance(string, unicode):
        return string.encode('utf8')
    else:
        return string

def flatten(lst):
    for elem in lst:
        if isinstance(elem, list) or isinstance(elem, tuple):
            for i in flatten(elem):
                yield i
        else:
            yield elem

def get_values(object, fields):
    value_dict = {}
    for field in fields:
        value = getattr(object, field)
        if value.__class__.__name__ == 'ManyRelatedManager':
            value = [item.id for item in value.all()]
        elif value.__class__.__name__ == 'datetime':
            value = value.date()
        value_dict[field] = value
    return value_dict

def get_dict(fields, values):
    value_dict = {}
    for field in fields:
        value = from_utf8(values[field])
        if isinstance(value, list):
            value = [item.id for item in value]
        else:
            value_dict[field] = value
    return value_dict

def set_values(object, fields, values):
    for field in fields:
        setattr(object, field, from_utf8(values[field]))

def language_list():
    return dict(settings.LANGUAGES).keys()

class PositionDict(dict):
    """
    Dictionary which is used for the content and title objects.
    It is designed to be used in a Django template.
    e.g.: {{ content }} - displays the default page content
          {{ content.left }} - displays the page content at the left position
    """

    def __init__(self, default):
        super(dict, self).__init__()
        self.default = default

    def __unicode__(self):
        return self.get(self.default)

def resolve_dotted_path(path):
    dot = path.rindex('.')
    mod_name, func_name = path[:dot], path[dot+1:]
    return getattr(__import__(mod_name, {}, {}, ['']), func_name)
