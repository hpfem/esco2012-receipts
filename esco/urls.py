from django.conf.urls.defaults import patterns, include
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^', include('esco.site.views')),
    (r'^admin/', include(admin.site.urls)),
)

