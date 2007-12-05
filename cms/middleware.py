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
