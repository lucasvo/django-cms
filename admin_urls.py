from django.conf.urls.defaults import *

urlpatterns = patterns('cms',
    (r'^cms/page/add/$', 'admin_views.page_add_edit'),
    (r'^cms/page/([0-9]+)/$', 'admin_views.page_add_edit'),
    (r'^cms/page/([0-9]+)/json/$', 'admin_views.page_add_edit'),
    (r'^cms/page/([0-9]+)/preview/$', 'admin_views.page_preview'),
    (r'^cms/page/$', 'admin_views.navigation'),
    (r'^cms/pagecontent/json/$', 'admin_views.pagecontent_json'),
)

