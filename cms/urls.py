from django.conf.urls.defaults import *

urlpatterns = patterns('cms',
    (r'^search/', 'views.search'),
    (r'', 'views.handler'),
)
