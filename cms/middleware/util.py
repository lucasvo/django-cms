import datetime
import re

HTML_CONTENT_TYPE_RE = re.compile(r'^text/html\b')

class XHTMLToHTMLMiddleware:
    def process_response(self, request, response):
        if HTML_CONTENT_TYPE_RE.match(response['Content-Type']):
            response.content = response.content.replace(' />', '>')
        return response

class BenchmarkMiddleware:
    def process_request(self, request):
        self.start = datetime.datetime.now()

    def process_response(self, request, response):
        if response.status_code == 200:
            stop = datetime.datetime.now()
            delta = stop-self.start
            print 'Processing time:', '%d.%06d' % (delta.seconds, delta.microseconds)
        return response
