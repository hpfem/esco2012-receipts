from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^events/esco-2010/', include('esco.site.views')),
    (r'^events/esco-2010/admin/', include(admin.site.urls)),
)

