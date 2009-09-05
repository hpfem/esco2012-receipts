from django.conf.urls.defaults import patterns, include
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^events/esco-2010/', include('esco.site.views')),
    (r'^events/esco-2010/admin/', include(admin.site.urls)),
)

handler404 = 'esco.site.views.handler404'
handler500 = 'esco.site.views.handler500'

