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
    (r'^dates/$', 'dates_view'),
    (r'^venue/$', 'venue_view'),
    (r'^payment/$', 'payment_view'),
    (r'^accommodation/$', 'accommodation_view'),
    (r'^travel/$', 'travel_view'),

    (r'^account/login/$', 'account_login_view'),
    (r'^account/logout/$', 'account_logout_view'),

    (r'^account/delete/$', 'account_delete_view'),
    (r'^account/delete/success/$', 'account_delete_success_view'),

    (r'^account/register/$', 'account_register_view'),
    (r'^account/register/success/$', 'account_register_success_view'),

    (r'^account/password/change/$', 'account_password_change_view'),
    (r'^account/password/change/success/$', 'account_password_change_success_view'),

    (r'^account/password/remind/$', 'account_password_remind_view'),
    (r'^account/password/remind/success/$', 'account_password_remind_success_view'),

    (r'^account/modify/$', 'account_modify_view'),

    (r'^account/abstracts/$', 'abstracts_view'),
    (r'^account/abstracts/add/$', 'abstracts_add_view'),
    (r'^account/abstracts/modify/(\d+)/$', 'abstracts_modify_view'),
    (r'^account/abstracts/delete/(\d+)/$', 'abstracts_delete_view'),
)

def _render_to_response(page, request, args=None):
    return render_to_response(page, RequestContext(request, args), mimetype="text/html")

def index_view(request, **args):
    return _render_to_response('base.html', request, args)

def topics_view(request, **args):
    return _render_to_response('topics.html', request)

def keynote_view(request, **args):
    return _render_to_response('keynote.html', request)

def committees_view(request, **args):
    return _render_to_response('committees.html', request)

def dates_view(request, **args):
    return _render_to_response('dates.html', request)

def venue_view(request, **args):
    return _render_to_response('venue.html', request)

def payment_view(request, **args):
    return _render_to_response('payment.html', request)

def accommodation_view(request, **args):
    return _render_to_response('accommodation.html', request)

def travel_view(request, **args):
    return _render_to_response('travel.html', request)

def account_login_view(request, **args):
    next = request.REQUEST.get('next', '/esco/')

    if request.method == 'POST':
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()
        else:
            return HttpResponse("Please enable cookies and try again.")

        form = LoginForm(request.POST)

        if form.is_valid():
            login(request, form.user)

            if not form.cleaned_data['remember']:
                request.session.set_expiry(0)
                request.session.save()

            request.session.set_test_cookie()

            return HttpResponsePermanentRedirect(next)
    else:
        form = LoginForm()

    request.session.set_test_cookie()

    local_args = {'form': form, 'next': next}
    local_args.update(args)

    return _render_to_response('login.html', request, local_args)

@login_required
def account_logout_view(request, **args):
    logout(request)

    return HttpResponsePermanentRedirect('/esco/')

@login_required
def account_delete_view(request, **args):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()

        return HttpResponsePermanentRedirect('/esco/account/delete/success/')
    else:
        return _render_to_response('delete.html', request, args)

def account_delete_success_view(request, **args):
    return index_view(request, message="Your account has been removed.")

def account_register_view(request, **args):
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

            return HttpResponsePermanentRedirect('/esco/account/register/success/')
    else:
        form = RegistrationForm()

    return _render_to_response('register.html', request, {'form': form})

def account_register_success_view(request, **args):
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

            return HttpResponsePermanentRedirect('/esco/account/password/change/success/')
    else:
        form = PasswordForm()

    return _render_to_response('password.html', request, {'form': form})

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

            return HttpResponsePermanentRedirect('/esco/account/password/remind/success/')
    else:
        form = ReminderForm()

    return _render_to_response('reminder.html', request, {'form': form})

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

            return HttpResponsePermanentRedirect('/esco/account/modify/')
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

    return _render_to_response('modify.html', request, {'form': form})

@login_required
def abstracts_view(request, **args):
    return _render_to_response('abstracts.html', request,
        {'abstracts': UserAbstract.objects.filter(user=request.user)})

@login_required
def abstracts_add_view(request, **args):
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
                return HttpResponsePermanentRedirect('/esco/account/abstracts/add/failed/')

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

            return HttpResponsePermanentRedirect('/esco/account/abstracts/')
    else:
        form = UploadAbstractForm()

    return _render_to_response('abstracts_add.html', request, {'form': form, 'text': 'Submit'})

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
                    return HttpResponsePermanentRedirect('/esco/account/abstracts/add/failed/')

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

            return HttpResponsePermanentRedirect('/esco/account/abstracts/')
    else:
        form = ModifyAbstractForm({'abstract_title': abstract.title})

    return _render_to_response('abstracts_add.html', request, {'form': form, 'text': 'Modify'})

@login_required
def abstracts_delete_view(request, abstract_id, **args):
    try:
        abstract = UserAbstract.objects.get(id=abstract_id)

        os.remove(os.path.join(ABSTRACTS_PATH,
                               abstract.digest+'.tex'))
        abstract.delete()
    except UserAbstract.DoesNotExist:
        pass

    return HttpResponsePermanentRedirect('/esco/account/abstracts/')

