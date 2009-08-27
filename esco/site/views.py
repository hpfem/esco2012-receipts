from django.conf.urls.defaults import patterns

from django.http import HttpResponse, Http404
from django.template import Context, loader

from django.shortcuts import (
    get_object_or_404, get_list_or_404, render_to_response,
)

urlpatterns = patterns('esco.site.views',
    (r'^$', 'index_view'),

    (r'^login/$', 'login_view'),
    (r'^logout/$', 'logout_view'),
    (r'^register/$', 'register_view'),

    (r'^topics/$', 'topics_view'),
    (r'^keynote/$', 'keynote_view'),
    (r'^committees/$', 'committees_view'),
    (r'^dates/$', 'dates_view'),
    (r'^venue/$', 'venue_view'),
    (r'^payment/$', 'payment_view'),
    (r'^accommodation/$', 'accommodation_view'),
    (r'^travel/$', 'travel_view'),
)

def index_view(request):
    return render_to_response('base.html', {}, mimetype="application/xhtml+xml")

def login_view(request):
    pass

def logout_view(request):
    pass

def register_view(request):
    pass

def topics_view(request):
    return render_to_response('topics.html', {}, mimetype="application/xhtml+xml")

def keynote_view(request):
    return render_to_response('keynote.html', {}, mimetype="application/xhtml+xml")

def committees_view(request):
    return render_to_response('committees.html', {}, mimetype="application/xhtml+xml")

def dates_view(request):
    return render_to_response('dates.html', {}, mimetype="application/xhtml+xml")

def venue_view(request):
    return render_to_response('venue.html', {}, mimetype="application/xhtml+xml")

def payment_view(request):
    return render_to_response('payment.html', {}, mimetype="application/xhtml+xml")

def accommodation_view(request):
    return render_to_response('accommodation.html', {}, mimetype="application/xhtml+xml")

def travel_view(request):
    return render_to_response('travel.html', {}, mimetype="application/xhtml+xml")

