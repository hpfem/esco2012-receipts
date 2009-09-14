from django.conf.urls.defaults import patterns

from django.http import HttpResponse, HttpResponsePermanentRedirect
from django.template import RequestContext, Context, loader

from django.shortcuts import render_to_response

from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

from esco.site.models import UserProfile, UserAbstract

from esco.site.forms import LoginForm, ReminderForm, RegistrationForm
from esco.site.forms import ChangePasswordIfAuthForm, ChangePasswordNoAuthForm
from esco.site.forms import UserProfileForm, SubmitAbstractForm, ModifyAbstractForm

from esco.settings import MIN_PASSWORD_LEN, ABSTRACTS_PATH

import os
import hashlib
import datetime

urlpatterns = patterns('esco.site.views',
    (r'^$',      'index_view'),
    (r'^home/$', 'index_view'),

    (r'^topics/$',        '_render_template', {'template': 'content/topics.html'}),
    (r'^keynote/$',       '_render_template', {'template': 'content/keynote.html'}),
    (r'^committees/$',    '_render_template', {'template': 'content/committees.html'}),
    (r'^payment/$',       '_render_template', {'template': 'content/payment.html'}),
    (r'^venue/$',         '_render_template', {'template': 'content/venue.html'}),
    (r'^accommodation/$', '_render_template', {'template': 'content/accommodation.html'}),
    (r'^travel/$',        '_render_template', {'template': 'content/travel.html'}),
    (r'^postconf/$',      '_render_template', {'template': 'content/postconf.html'}),
    (r'^contact/$',       '_render_template', {'template': 'content/contact.html'}),

    (r'^account/$',       '_render_template', {'template': 'account/account.html'}),

    (r'^account/login/$', 'account_login_view'),
    (r'^account/logout/$', 'account_logout_view'),

    (r'^account/create/$', 'account_create_view'),
    (r'^account/create/success/$', 'account_login_view',
        {'message': 'New account was created. You can login now.'}),

    (r'^account/delete/$', 'account_delete_view'),
    (r'^account/delete/success/$', 'index_view',
        {'message': 'Your account was successfully removed.'}),

    (r'^account/password/change/$', 'account_password_change_view'),
    (r'^account/password/change/success/$', 'index_view',
        {'message': 'Your password was successfully changed.'}),

    (r'^account/password/remind/$', 'account_password_remind_view'),
    (r'^account/password/remind/success/$', 'index_view',
        {'message': 'New auto-generated password was sent to you.'}),

    (r'^account/profile/$', 'account_profile_view'),

    (r'^account/abstracts/$', 'abstracts_view'),
    (r'^account/abstracts/submit/$', 'abstracts_submit_view'),
    (r'^account/abstracts/submit/failed/$', 'abstracts_view',
        {'message': 'The same abstract was already submitted.'}),
    (r'^account/abstracts/modify/(\d+)/$', 'abstracts_modify_view'),
    (r'^account/abstracts/modify/failed/$', 'abstracts_view',
        {'message': 'You must specify both *.tex and *.pdf files.'}),
    (r'^account/abstracts/delete/(\d+)/$', 'abstracts_delete_view'),
)

def _render_to_response(page, request, args=None):
    return render_to_response(page, RequestContext(request, args))

def _render_template(request, **args):
    return _render_to_response(args.get('template'), request)

def handler404(request):
    return _render_to_response('errors/404.html', request)

def handler500(request):
    return _render_to_response('errors/500.html', request)

def index_view(request, **args):
    return _render_to_response('base.html', request, args)

def account_login_view(request, **args):
    next = request.REQUEST.get('next', '/events/esco-2010/account/')

    if request.method == 'POST':
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()
        else:
            return HttpResponse("Please enable cookies and try again.")

        form = LoginForm(request.POST)

        if form.is_valid():
            login(request, form.user)
            request.session.set_test_cookie()

            return HttpResponsePermanentRedirect(next)
    else:
        form = LoginForm()

    request.session.set_test_cookie()

    local_args = {'form': form, 'next': next}
    local_args.update(args)

    return _render_to_response('account/login.html', request, local_args)

@login_required
def account_logout_view(request, **args):
    logout(request)

    return HttpResponsePermanentRedirect('/events/esco-2010/')

@login_required
def account_delete_view(request, **args):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()

        return HttpResponsePermanentRedirect('/events/esco-2010/account/delete/success/')
    else:
        return _render_to_response('account/delete.html', request, args)

def account_create_view(request, **args):
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

            return HttpResponsePermanentRedirect('/events/esco-2010/account/create/success/')
    else:
        form = RegistrationForm()

    return _render_to_response('account/create.html', request, {'form': form})

def account_password_change_view(request, **args):
    if request.method == 'POST':
        if request.user.is_authenticated():
            form = ChangePasswordIfAuthForm(request.POST)
        else:
            form = ChangePasswordNoAuthForm(request.POST)

        if form.is_valid():
            password = form.cleaned_data['password_new']

            if request.user.is_authenticated():
                request.user.set_password(password)
                request.user.save()
            else:
                form.user.set_password(password)
                form.user.save()

            return HttpResponsePermanentRedirect('/events/esco-2010/account/password/change/success/')
    else:
        if request.user.is_authenticated():
            form = ChangePasswordIfAuthForm()
        else:
            form = ChangePasswordNoAuthForm()

    return _render_to_response('password/change.html', request, {'form': form})

def account_password_remind_view(request, **args):
    if request.method == 'POST':
        form = ReminderForm(request.POST)

        if form.is_valid():
            password = User.objects.make_random_password(length=MIN_PASSWORD_LEN)

            user = User.objects.get(username=form.cleaned_data['username'])
            user.set_password(password)
            user.save()

            template = loader.get_template('e-mails/reminder.txt')
            body = template.render(Context({'user': user, 'password': password}))

            user.email_user("ESCO 2010 - Password reminder notification", body)

            return HttpResponsePermanentRedirect('/events/esco-2010/account/password/remind/success/')
    else:
        form = ReminderForm()

    return _render_to_response('password/remind.html', request, {'form': form})

@login_required
def account_profile_view(request, **args):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)

        if form.is_valid():
            try:
                profile = request.user.get_profile()
            except UserProfile.DoesNotExist:
                profile = UserProfile(user=request.user)

            for field in form.base_fields.iterkeys():
                if field == 'first_name':
                    first_name = form.cleaned_data.get('first_name')

                    if first_name and first_name != request.user.first_name:
                        request.user.first_name = first_name
                        request.user.save()
                elif field == 'last_name':
                    last_name = form.cleaned_data.get('last_name')

                    if last_name and last_name != request.user.last_name:
                        request.user.last_name = last_name
                        request.user.save()
                else:
                    value = form.cleaned_data.get(field)

                    if value != getattr(profile, field):
                        setattr(profile, field, value)

            profile.save()

            return HttpResponsePermanentRedirect('/events/esco-2010/account/profile/')
    else:
        data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        }

        try:
            profile = request.user.get_profile()

            for field in UserProfileForm.base_fields.iterkeys():
                if field in ['first_name', 'last_name']:
                    continue

                if field in ['arrival', 'departure']:
                    data[field] = getattr(profile, field).strftime('%d/%m/%Y')
                else:
                    data[field] = getattr(profile, field)
        except UserProfile.DoesNotExist:
            pass

        form = UserProfileForm(initial=data)

    return _render_to_response('account/profile.html', request, {'form': form})

@login_required
def abstracts_view(request, **args):
    return _render_to_response('abstracts/abstracts.html', request,
        {'abstracts': UserAbstract.objects.filter(user=request.user),
         'message': args.get('message', None)})

class FileExistsError(Exception):
    pass

def _file_digest(request, ext):
    sha1 = hashlib.new('sha1')
    ifile = request.FILES['abstract_' + ext]

    for chunk in ifile.chunks():
        sha1.update(chunk)

    return sha1.hexdigest()

def _write_file(request, digest, ext):
    path = os.path.join(ABSTRACTS_PATH, digest + '.' + ext)

    if os.path.exists(path):
        raise FileExistsError

    ifile = request.FILES['abstract_' + ext]
    ofile = open(path, 'wb')

    for chunk in ifile.chunks():
        ofile.write(chunk)

    ofile.close()

    return os.path.getsize(path)

@login_required
def abstracts_submit_view(request, **args):
    if request.method == 'POST':
        form = SubmitAbstractForm(request.POST, request.FILES)

        if form.is_valid():
            digest_tex = _file_digest(request, 'tex')
            digest_pdf = _file_digest(request, 'pdf')

            try:
                size_tex = _write_file(request, digest_tex, 'tex')
                size_pdf = _write_file(request, digest_tex, 'pdf')
            except FileExistsError:
                return HttpResponsePermanentRedirect('/events/esco-2010/account/abstracts/submit/failed/')

            date = datetime.datetime.today()

            abstract = UserAbstract(
                user=request.user,
                title=form.cleaned_data['title'],
                digest_tex=digest_tex,
                digest_pdf=digest_pdf,
                size_tex=size_tex,
                size_pdf=size_pdf,
                submit_date=date,
                modify_date=date,
            )

            abstract.save()

            return HttpResponsePermanentRedirect('/events/esco-2010/account/abstracts/')
    else:
        form = SubmitAbstractForm()

    return _render_to_response('abstracts/submit.html', request, {'form': form})

@login_required
def abstracts_modify_view(request, abstract_id, **args):
    abstract = UserAbstract.objects.get(id=abstract_id)

    if request.method == 'POST':
        form = ModifyAbstractForm(request.POST, request.FILES)

        if form.is_valid():
            date = datetime.datetime.today()

            if 'abstract_tex' in request.FILES and 'abstract_pdf' in request.FILES:
                digest_tex = _file_digest(request, 'tex')
                digest_pdf = _file_digest(request, 'pdf')

                try:
                    size_tex = _write_file(request, digest_tex, 'tex')
                    size_pdf = _write_file(request, digest_tex, 'pdf')
                except FileExistsError:
                    return HttpResponsePermanentRedirect('/events/esco-2010/account/abstracts/submit/failed/')

                abstract.digest_tex = digest_tex
                abstract.digest_pdf = digest_pdf
                abstract.size_tex = size_tex
                abstract.size_pdf = size_pdf
                abstract.modify_date = date
                abstract.save()
            elif 'abstract_tex' in request.FILES or 'abstract_pdf' in request.FILES:
                return HttpResponsePermanentRedirect('/events/esco-2010/account/abstracts/modify/failed/')

            title = form.cleaned_data.get('title')

            if title and title != abstract.title:
                abstract.modify_date = date
                abstract.title = title
                abstract.save()

            return HttpResponsePermanentRedirect('/events/esco-2010/account/abstracts/')
    else:
        form = ModifyAbstractForm(initial={'title': abstract.title})

    return _render_to_response('abstracts/modify.html', request, {'form': form})

@login_required
def abstracts_delete_view(request, abstract_id, **args):
    try:
        abstract = UserAbstract.objects.get(id=abstract_id)

        os.remove(os.path.join(ABSTRACTS_PATH,
                               abstract.digest_tex+'.tex'))
        os.remove(os.path.join(ABSTRACTS_PATH,
                               abstract.digest_tex+'.pdf'))
        abstract.delete()
    except UserAbstract.DoesNotExist:
        pass

    return HttpResponsePermanentRedirect('/events/esco-2010/account/abstracts/')

