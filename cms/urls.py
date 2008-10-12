from django.conf.urls.defaults import *
from cms.views import handler, search

urlpatterns = patterns('',
    url(r'^search/', search, name='cms_search'),
    url(r'^.*/$', handler),
    url(r'^$', handler, name='cms_root'),
)
