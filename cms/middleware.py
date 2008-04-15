import datetime
import re

re_ct_html = re.compile(r'^text/html\b')

class XHTMLToHTMLMiddleware:
    def process_response(self, request, response):
        if re_ct_html.match(response['Content-Type']):
            response.content = response.content.replace(' />', '>')
        return response

class BenchmarkMiddleware:
    def process_request(self, request):
        self.start = datetime.datetime.now()
        print
    def process_response(self, request, response):
        if response.status_code == 200:
            stop = datetime.datetime.now()
            delta = stop-self.start
            print 'Processing time:', '%d.%06d' % (delta.seconds, delta.microseconds)
        return response

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

_thread_locals = local()
def get_current_user():
    return getattr(_thread_locals, 'user', None)

class ThreadLocals(object):
    """Middleware that gets various objects from the
    request object and saves them in thread local storage."""
    def process_request(self, request):
        _thread_locals.user = getattr(request, 'user', None)
