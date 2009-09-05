from django import forms

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from django.core.exceptions import ObjectDoesNotExist

from esco.contrib.captcha import CaptchaField
from esco.settings import MIN_PASSWORD_LEN, CHECK_STRENGTH

class LoginForm(forms.Form):
    """Form for logging in users. """

    username = forms.CharField(
        required  = True,
        label     = "Login",
    )

    password = forms.CharField(
        required  = True,
        label     = "Password",
        widget    = forms.PasswordInput(),
    )

    def clean(self):
        """Authenticate and login user, if possible. """
        cleaned_data = self.cleaned_data

        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            self.user = authenticate(username=username,
                                     password=password)

            if self.user is not None:
                if self.user.is_active:
                    return cleaned_data
                else:
                    raise forms.ValidationError('Your account has been disabled.')

        raise forms.ValidationError('Wrong login or password. Please try again.')

class ReminderForm(forms.Form):
    """Password reminder form. """

    username = forms.CharField(
        required = True,
        label    = "Login",
    )
    captcha = CaptchaField(
        required = True,
        label    = "Security Code",
    )

    def clean_username(self):
        """Make sure `username` is registred in the system. """
        username = self.cleaned_data['username']

        try:
            User.objects.get(username=username)
        except ObjectDoesNotExist:
            raise forms.ValidationError('Selected user does not exist.')

        return username

_digit = set(map(chr, range(48, 58)))
_upper = set(map(chr, range(65, 91)))
_lower = set(map(chr, range(97,123)))

class RegistrationForm(forms.Form):
    """Form for creating new users. """

    username = forms.EmailField(
        required   = True,
        label      = "E-mail",
        help_text  = "This will be your login.",
    )
    username_again = forms.EmailField(
        required   = True,
        label      = "E-mail (Again)",
        help_text  = "Make sure this is a valid E-mail address.",
    )

    password = forms.CharField(
        required   = True,
        label      = "Password",
        widget     = forms.PasswordInput(),
        help_text  = "Use lower and upper case letters, numbers etc.",
    )
    password_again = forms.CharField(
        required   = True,
        label      = "Password (Again)",
        widget     = forms.PasswordInput(),
    )

    first_name = forms.CharField(
        required   = True,
        label      = "First Name",
        help_text  = "Enter your first name using Unicode character set.",
    )
    last_name = forms.CharField(
        required   = True,
        label      = "Last Name",
        help_text  = "Enter your last name using Unicode character set.",
    )

    captcha = CaptchaField(
        required = True,
        label    = "Security Code",
    )

    def clean_username(self):
        """Make sure `login` is unique in the system. """
        username = self.cleaned_data['username']

        try:
            User.objects.get(username=username)
        except ObjectDoesNotExist:
            return username

        raise forms.ValidationError('Login is already in use.')

    def clean_username_again(self):
        """Make sure user verified `login` he entered. """
        if 'username' in self.cleaned_data:
            username       = self.cleaned_data['username']
            username_again = self.cleaned_data['username_again']

            if username == username_again:
                return username
        else:
            return None

        raise forms.ValidationError('Logins do not match.')

    def clean_password(self):
        """Make sure `password` isn't too easy to break. """
        password = self.cleaned_data['password']

        if CHECK_STRENGTH:
            if len(password) < MIN_PASSWORD_LEN:
                raise forms.ValidationError('Password must have at least %i characters.' % MIN_PASSWORD_LEN)

            symbols = set(password)

            if (not _digit & symbols) or (not _upper & symbols) or (not _lower & symbols):
                raise forms.ValidationError('Password is too week. Invent better one.')

        return password

    def clean_password_again(self):
        """Make sure user verified `password` he entered. """
        if 'password' in self.cleaned_data:
            password       = self.cleaned_data['password']
            password_again = self.cleaned_data['password_again']

            if password == password_again:
                return password
        else:
            return None

        raise forms.ValidationError('Passwords do not match.')

class PasswordForm(forms.Form):
    """Password change form. """

    username = forms.CharField(
        required   = True,
        label      = "Login",
    )

    password_old = forms.CharField(
        required   = True,
        label      = "Old Password",
        widget     = forms.PasswordInput(),
        help_text  = "Enter your old password for security reason.",
    )

    password_new = forms.CharField(
        required   = True,
        label      = "New Password",
        widget     = forms.PasswordInput(),
        help_text  = "Use lower and upper case letters, numbers etc.",
    )

    password_new_again = forms.CharField(
        required   = True,
        label      = "New Password (Again)",
        widget     = forms.PasswordInput(),
    )

    captcha = CaptchaField(
        required  = True,
        label     = "Security Code",
    )

    def clean_username(self):
        """Make sure `username` is registred in the system. """
        username = self.cleaned_data['username']

        try:
            User.objects.get(username=username)
        except ObjectDoesNotExist:
            raise forms.ValidationError('Selected user does not exist.')

        return username

    def clean_password_old(self):
        """Make sure user can authenticate with `password_old`. """
        cleaned_data = self.cleaned_data

        username     = cleaned_data.get('username')
        password_old = cleaned_data.get('password_old')

        if username and password_old:
            self.user = authenticate(username=username,
                                     password=password_old)

            if self.user is not None:
                return password_old

        raise forms.ValidationError('Invalid password.')

    def clean_password_new(self):
        """Make sure `password_new` isn't too easy to break. """
        cleaned_data = self.cleaned_data

        password_old = cleaned_data.get('password_old')
        password_new = cleaned_data.get('password_new')

        if password_old == password_new:
            raise forms.ValidationError("New password dosen't differ from the old one.")

        if CHECK_STRENGTH:
            if len(password_new) < MIN_PASSWORD_LEN:
                raise forms.ValidationError('Password must have at least %i characters.' % MIN_PASSWORD_LEN)

            symbols = set(password_new)

            if (not _digit & symbols) or (not _upper & symbols) or (not _lower & symbols):
                raise forms.ValidationError('Password is too week. Invent better one.')

        return password_new

    def clean_password_new_again(self):
        """Make sure user verified `password` he entered. """
        if 'password_new' in self.cleaned_data:
            password_new       = self.cleaned_data['password_new']
            password_new_again = self.cleaned_data['password_new_again']

            if password_new == password_new_again:
                return password_new
        else:
            return None

        raise forms.ValidationError('Passwords do not match.')

class AccountModifyForm(forms.Form):
    """Account modification form. """

    first_name = forms.CharField(
        required  = True,
        label     = "First Name",
        help_text = "Enter your first name using Unicode character set.",
    )

    last_name = forms.CharField(
        required  = True,
        label     = "Last Name",
        help_text = "Enter your last name using Unicode character set.",
    )

    institution = forms.CharField(
        required  = False,
        label     = "Institution",
        help_text = "e.g. University of Nevada",
    )

    address = forms.CharField(
        required  = False,
        label     = "Address",
        help_text = "You can use Unicode character set.",
    )

    city = forms.CharField(
        required  = False,
        label     = "City",
        help_text = "You can use Unicode character set.",
    )

    postal_code = forms.CharField(
        required  = False,
        label     = "Postal Code",
        help_text = "",
    )

    country = forms.CharField(
        required  = False,
        label     = "Country",
        help_text = "Enter english country name.",
    )

    phone = forms.CharField(
        required  = False,
        label     = "Phone Number",
        help_text = "Enter your phone number, e.g. +48 123 456 789",
    )

class UploadAbstractForm(forms.Form):

    abstract_title = forms.CharField(
        required  = True,
        label     = "Title",
        help_text = "Enter full title of your work.",
    )

    abstract_file = forms.FileField(
        required  = True,
        label     = "File",
        help_text = "Select a text file with your abstract. Don't upload compressed archives.",
    )

class ModifyAbstractForm(forms.Form):

    abstract_title = forms.CharField(
        required  = True,
        label     = "Title",
        help_text = "Enter full title of your work.",
    )

    abstract_file = forms.FileField(
        required  = False,
        label     = "File",
        help_text = "Select a text file with your abstract. Don't upload compressed archives.",
    )

class AbstractAuthorForm(forms.Form):

    first_name = forms.CharField(
        required   = True,
        label      = "First Name",
        help_text  = "Enter author's first name using Unicode character set.",
    )

    last_name = forms.CharField(
        required   = True,
        label      = "Last Name",
        help_text  = "Enter author's last name using Unicode character set.",
    )

