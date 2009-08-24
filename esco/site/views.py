from django.conf.urls.defaults import patterns

from django.http import HttpResponse, Http404
from django.template import Context, loader

from django.shortcuts import (
    get_object_or_404, get_list_or_404,
)

urlpatterns = patterns('esco.site.views',
    (r'^$', 'index'),

    #(r'^login/$', ),
    #(r'^logout/$', ),
    #(r'^register/$', ),

    #(r'^home/$', ),
    #(r'^committees/$', ),
    #(r'^invited_speakers/$', ),
    #(r'^call_for_papers/$', ),
    #(r'^programme/$', ),
    #(r'^payment/$', ),
    #(r'^accomodation/$', ),
    #(r'^travel_information/$', ),
)

def index(request):
    template = loader.get_template('index.html')

    c = Context({

    })

    return HttpResponse(template.render(c))

