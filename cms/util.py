from django.conf import settings

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
    return [l[0] for l in settings.LANGUAGES]
