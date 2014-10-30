from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',

    url(r'^admin/', include(admin.site.urls)),

    # Owners
    url(r'^api/owners/register/$', 'smart.views.register', name='owners_register'),
    url(r'^api/owners/login/$', 'smart.views.log_in', name='owners_login'),

    #Devices
    url(r'^api/devices/add/$', 'smart.views.devices_add', name='devices_add'),
    url(r'^api/devices/about/more/$', 'smart.views.devices_about_more', name='devices_about_more'),
    url(r'^api/devices/remove/$', 'smart.views.devices_remove', name='devices_remove'),

    #Events
    url(r'^api/events/add/$', 'smart.views.events_add', name='devices_add'),
    url(r'^api/events/more/$', 'smart.views.events_more', name='events_more'),

    url(r'^api/events/ended/$', 'smart.views.events_ended', name='events_ended'),
)
