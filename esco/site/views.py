from django.conf.urls.defaults import patterns

from django.http import HttpResponse, HttpResponsePermanentRedirect
from django.template import RequestContext, Context, loader

from django.shortcuts import render_to_response

from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

from esco.site.forms import LoginForm, ReminderForm, RegistrationForm, PasswordForm
from esco.site.forms import AccountModifyForm, UploadAbstractForm, ModifyAbstractForm
from esco.site.models import UserProfile, UserAbstract
from esco.settings import MIN_PASSWORD_LEN, ABSTRACTS_PATH

import os
import hashlib
import datetime

urlpatterns = patterns('esco.site.views',
    (r'^$', 'index_view'),
    (r'^home/$', 'index_view'),

    (r'^topics/$', 'topics_view'),
    (r'^keynote/$', 'keynote_view'),
    (r'^committees/$', 'committees_view'),
    (r'^submission/$', 'submission_view'),
    (r'^venue/$', 'venue_view'),
    (r'^payment/$', 'payment_view'),
    (r'^accommodation/$', 'accommodation_view'),
    (r'^travel/$', 'travel_view'),

    (r'^account/login/$', 'account_login_view'),
    (r'^account/logout/$', 'account_logout_view'),

    (r'^account/delete/$', 'account_delete_view'),
    (r'^account/delete/success/$', 'account_delete_success_view'),

    (r'^account/create/$', 'account_create_view'),
    (r'^account/create/success/$', 'account_create_success_view'),

    (r'^account/password/change/$', 'account_password_change_view'),
    (r'^account/password/change/success/$', 'account_password_change_success_view'),

    (r'^account/password/remind/$', 'account_password_remind_view'),
    (r'^account/password/remind/success/$', 'account_password_remind_success_view'),

    (r'^account/modify/$', 'account_modify_view'),

    (r'^account/abstracts/$', 'abstracts_view'),
    (r'^account/abstracts/submit/$', 'abstracts_submit_view'),
    (r'^account/abstracts/submit/failed/$', 'abstracts_submit_failed_view'),
    (r'^account/abstracts/modify/(\d+)/$', 'abstracts_modify_view'),
    (r'^account/abstracts/modify/failed/$', 'abstracts_modify_failed_view'),
    (r'^account/abstracts/delete/(\d+)/$', 'abstracts_delete_view'),
)

def _render_to_response(page, request, args=None):
    return render_to_response(page, RequestContext(request, args), mimetype="text/html")

def handler404(request):
    return _render_to_response('errors/404.html', request)

def handler500(request):
    return _render_to_response('errors/500.html', request)

def index_view(request, **args):
    return _render_to_response('base.html', request, args)

def topics_view(request, **args):
    return _render_to_response('content/topics.html', request)

def keynote_view(request, **args):
    return _render_to_response('content/keynote.html', request)

def committees_view(request, **args):
    return _render_to_response('content/committees.html', request)

def submission_view(request, **args):
    return _render_to_response('content/submission.html', request)

def venue_view(request, **args):
    return _render_to_response('content/venue.html', request)

def payment_view(request, **args):
    return _render_to_response('content/payment.html', request)

def accommodation_view(request, **args):
    return _render_to_response('content/accommodation.html', request)

def travel_view(request, **args):
    return _render_to_response('content/travel.html', request)

def account_login_view(request, **args):
    next = request.REQUEST.get('next', '/events/esco-2010/')

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

def account_delete_success_view(request, **args):
    return index_view(request, message="Your account has been removed.")

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

            profile = UserProfile(user=user)
            profile.save()

            return HttpResponsePermanentRedirect('/events/esco-2010/account/create/success/')
    else:
        form = RegistrationForm()

    return _render_to_response('account/create.html', request, {'form': form})

def account_create_success_view(request, **args):
    return account_login_view(request, registred=True)

def account_password_change_view(request, **args):
    if request.method == 'POST':
        post = request.POST.copy()

        if request.user.is_authenticated():
            post['username'] = request.user.username

        form = PasswordForm(post)

        if form.is_valid():
            form.user.set_password(form.cleaned_data['password_new'])
            form.user.save()

            return HttpResponsePermanentRedirect('/events/esco-2010/account/password/change/success/')
    else:
        form = PasswordForm()

    return _render_to_response('password/change.html', request, {'form': form})

def account_password_change_success_view(request):
    return index_view(request, message="Your password was successfully changed.")

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

def account_password_remind_success_view(request, **args):
    return index_view(request, message="New auto-generated password was sent to you.")

@login_required
def account_modify_view(request, **args):
    if request.method == 'POST':
        form = AccountModifyForm(request.POST)

        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')

            if first_name and first_name != request.user.first_name:
                request.user.first_name = first_name
                request.user.save()

            last_name = form.cleaned_data.get('last_name')

            if last_name and last_name != request.user.last_name:
                request.user.last_name = last_name
                request.user.save()

            profile = request.user.get_profile()

            institution = form.cleaned_data.get('institution')

            if institution and institution != profile.institution:
                profile.institution = institution
                profile.save()

            institution = form.cleaned_data.get('institution')

            if institution and institution != profile.institution:
                profile.institution = institution
                profile.save()

            address = form.cleaned_data.get('address')

            if address and address != profile.address:
                profile.address = address
                profile.save()

            city = form.cleaned_data.get('city')

            if city and city != profile.city:
                profile.city = city
                profile.save()

            postal_code = form.cleaned_data.get('postal_code')

            if postal_code and postal_code != profile.postal_code:
                profile.postal_code = postal_code
                profile.save()

            country = form.cleaned_data.get('country')

            if country and country != profile.country:
                profile.country = country
                profile.save()

            phone = form.cleaned_data.get('phone')

            if phone and phone != profile.phone:
                profile.phone = phone
                profile.save()

            return HttpResponsePermanentRedirect('/events/esco-2010/account/modify/')
    else:
        try:
            profile = request.user.get_profile()
        except UserProfile.DoesNotExist:
            profile = UserProfile(user=request.user)
            profile.save()

        data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'institution': profile.institution,
            'address': profile.address,
            'city': profile.city,
            'postal_code': profile.postal_code,
            'country': profile.country,
            'phone': profile.phone,
        }

        form = AccountModifyForm(data)

    return _render_to_response('account/modify.html', request, {'form': form})

@login_required
def abstracts_view(request, **args):
    return _render_to_response('abstracts/abstracts.html', request,
        {'abstracts': UserAbstract.objects.filter(user=request.user)})

@login_required
def abstracts_submit_view(request, **args):
    if request.method == 'POST':
        form = UploadAbstractForm(request.POST, request.FILES)

        if form.is_valid():
            sha1 = hashlib.new('sha1')
            ifile = request.FILES['abstract_file']

            for chunk in ifile.chunks():
                sha1.update(chunk)

            digest = sha1.hexdigest()
            path = os.path.join(ABSTRACTS_PATH, digest+'.tex')

            if os.path.exists(path):
                return HttpResponsePermanentRedirect('/events/esco-2010/account/abstracts/submit/failed/')

            ofile = open(path, 'wb')

            for chunk in ifile.chunks():
                ofile.write(chunk)

            ofile.close()

            date = datetime.datetime.today()

            abstract = UserAbstract(
                user=request.user,
                title=form.cleaned_data['abstract_title'],
                digest=digest,
                size=os.path.getsize(path),
                upload_date=date,
                modify_date=date,
            )

            abstract.save()

            return HttpResponsePermanentRedirect('/events/esco-2010/account/abstracts/')
    else:
        form = UploadAbstractForm()

    return _render_to_response('abstracts/submit.html', request, {'form': form, 'text': 'Submit'})

@login_required
def abstracts_submit_failed_view(request, **args):
    return _render_to_response('abstracts/failed.html', request)

@login_required
def abstracts_modify_view(request, abstract_id, **args):
    abstract = UserAbstract.objects.get(id=abstract_id)

    if request.method == 'POST':
        form = ModifyAbstractForm(request.POST, request.FILES)

        if form.is_valid():
            date = datetime.datetime.today()

            if 'abstract_file' in request.FILES:
                sha1 = hashlib.new('sha1')
                ifile = request.FILES['abstract_file']

                for chunk in ifile.chunks():
                    sha1.update(chunk)

                digest = sha1.hexdigest()
                path = os.path.join(ABSTRACTS_PATH, digest+'.tex')

                if os.path.exists(path):
                    return HttpResponsePermanentRedirect('/events/esco-2010/account/abstracts/modify/failed/')

                abstract = UserAbstract.objects.get(user=request.user)
                os.remove(os.path.join(ABSTRACTS_PATH, abstract.digest+'.tex'))

                ofile = open(path, 'wb')

                for chunk in ifile.chunks():
                    ofile.write(chunk)

                ofile.close()

                abstract.modify_date = date
                abstract.digest = digest
                abstract.save()

            title = form.cleaned_data.get('abstract_title')

            if title and title != abstract.title:
                abstract.modify_date = date
                abstract.title = title
                abstract.save()

            return HttpResponsePermanentRedirect('/events/esco-2010/account/abstracts/')
    else:
        form = ModifyAbstractForm({'abstract_title': abstract.title})

    return _render_to_response('abstracts/submit.html', request, {'form': form, 'text': 'Modify'})

@login_required
def abstracts_modify_failed_view(request, **args):
    return _render_to_response('abstracts/failed.html', request)

@login_required
def abstracts_delete_view(request, abstract_id, **args):
    try:
        abstract = UserAbstract.objects.get(id=abstract_id)

        os.remove(os.path.join(ABSTRACTS_PATH,
                               abstract.digest+'.tex'))
        abstract.delete()
    except UserAbstract.DoesNotExist:
        pass

    return HttpResponsePermanentRedirect('/events/esco-2010/account/abstracts/')

