from django.conf.urls.defaults import *

urlpatterns = patterns('cms',
    (r'^search/', 'views.search'),
    (r'^$', 'views.handler'),
    (r'^([a-zA-Z0-9-_./]+)/', 'views.handler'),
)
