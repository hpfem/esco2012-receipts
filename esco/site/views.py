from django.conf.urls.defaults import patterns

from django.http import HttpResponsePermanentRedirect
from django.template import RequestContext

from django.shortcuts import render_to_response

from django.contrib.auth.models import User
from django.contrib.auth.views import login
from django.contrib.auth import logout

from esco.site.forms import LoginForm, ReminderForm, RegistrationForm

urlpatterns = patterns('esco.site.views',
    (r'^$', 'index_view'),

    (r'^topics/$', 'topics_view'),
    (r'^keynote/$', 'keynote_view'),
    (r'^committees/$', 'committees_view'),
    (r'^dates/$', 'dates_view'),
    (r'^venue/$', 'venue_view'),
    (r'^payment/$', 'payment_view'),
    (r'^accommodation/$', 'accommodation_view'),
    (r'^travel/$', 'travel_view'),

    (r'^profile/$', 'profile_view'),
    (r'^abstracts/$', 'abstracts_view'),

    (r'^login/$', 'login', {'template_name': 'login.html'}),
    (r'^logout/$', 'logout_view'),
    (r'^reminder/$', 'reminder_view'),
    (r'^register/$', 'register_view'),
)

def _render_to_response(page, request):
    return render_to_response(page, RequestContext(request), mimetype="application/xhtml+xml")

def index_view(request):
    return _render_to_response('base.html', request)

def topics_view(request):
    return _render_to_response('topics.html', request)

def keynote_view(request):
    return _render_to_response('keynote.html', request)

def committees_view(request):
    return _render_to_response('committees.html', request)

def dates_view(request):
    return _render_to_response('dates.html', request)

def venue_view(request):
    return _render_to_response('venue.html', request)

def payment_view(request):
    return _render_to_response('payment.html', request)

def accommodation_view(request):
    return _render_to_response('accommodation.html', request)

def travel_view(request):
    return _render_to_response('travel.html', request)

def profile_view(request):
    return _render_to_response('profile.html', request)

def abstracts_view(request):
    return _render_to_response('abstracts.html', request)

def logout_view(request):
    logout(request)
    return HttpResponsePermanentRedirect('/esco/')

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = User.objects.create_user(
                username = form.cleaned_data['username'],
                password = form.cleaned_data['password'],
                email    = form.cleaned_data['username'],
            )

            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']

            user.save()

            return HttpResponsePermanentRedirect('/esco/login/')
    else:
        form = RegistrationForm()

    return render_to_response('register.html', RequestContext(request,
        {'form': form}), mimetype="application/xhtml+xml")

def reminder_view(request):
    if request.method == 'POST':
        form = ReminderForm(request.POST)

        if form.is_valid():
            raise NotImplementedError('not yet')
    else:
        form = ReminderForm()

    return render_to_response('reminder.html', RequestContext(request,
        {'form': form}), mimetype="application/xhtml+xml")

