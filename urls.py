from django.conf.urls.defaults import *


urlpatterns = patterns('',
    url(r'^management/$', 'dashboard.views.management', name='pcp-dashboard-management'),
    url(r'^view/(?P<view_id>\d+)/$', 'dashboard.views.dashboard_view', name='pcp-dashboard-view'),
    url(r'^item/(?P<item_id>\d+)/$', 'dashboard.views.dashboard_item', name='pcp-dashboard-item'),    
    url(r'^save/$', 'dashboard.views.save_dashboard', name='pcp-dashboard-save'),
    url(r'^config/(?P<item_id>\d+)/$', 'dashboard.views.save_config', name='pcp-dashboard-config'),
    url(r'^remove/(?P<item_id>\d+)/$', 'dashboard.views.remove_item', name='pcp-dashboard-item_remove'),
)
