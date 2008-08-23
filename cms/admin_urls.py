from django.conf.urls.defaults import *
#from django.contrib.admin.views.main import change_stage, history, delete_stage
from django.views.generic.simple import redirect_to

urlpatterns = patterns('cms',
    (r'^cms/page/add/$', 'admin_views.page_add_edit'),
    (r'^cms/page/([0-9]+)/$', 'admin_views.page_add_edit'),
    (r'^cms/page/([0-9]+)/json/$', 'admin_views.page_add_edit'),
    (r'^cms/page/([0-9]+)/preview/$', 'admin_views.page_preview'),
    #(r'^(cms)/(page)/([0-9]+)/history/$', history),
    #(r'^(cms)/(page)/([0-9]+)/delete/$', delete_stage),
    #(r'^(cms)/(page)/([0-9]+)/add_ons/$', change_stage),
    (r'^cms/page/$', 'admin_views.navigation'),
    (r'^cms/pagecontent/json/$', 'admin_views.pagecontent_json'),
    # Handle add in related objects edit inline
    #(r'^cms/(?P<re_url>[a-zA-Z0-9-_./]+)/$', redirect_to, {'url': '/admin/%(re_url)s/?_popup=1'}),
)

