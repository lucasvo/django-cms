import datetime

from django.utils import simplejson
from django.http import HttpResponse
from django.conf import settings
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext as _

from cms.util import to_utf8, from_utf8

def admin_view(view_func):
    def _json(adminsite, request, *args, **kwargs):
        try:
            data = load(request.POST.get('json'))
            error = None
        except (TypeError, ValueError):
            return_data = {'error': _('Received invalid data.')}
        else:
            return_data = view_func(adminsite, request, data, *args, **kwargs)
        
        return HttpResponse(dump(return_data), 
                mimetype='text/plain; charset=%s' % settings.DEFAULT_CHARSET)

    return _json

def fix(d, f):
    if isinstance(d, str) or isinstance(d, unicode):
        return f(d)
    if isinstance(d, datetime.datetime):
        return smart_unicode(d) # TODO: What do we want to do with datetime objects?
    elif isinstance(d, list):
        for x in range(len(d)):
            d[x] = fix(d[x], f)
    elif isinstance(d, dict):
        for k, v in d.items():
            d[k] = fix(v, f)
    return d 

def load(data=''):
    return fix(simplejson.loads(data), from_utf8)

def dump(data): 
    return simplejson.dumps(fix(data, to_utf8))

