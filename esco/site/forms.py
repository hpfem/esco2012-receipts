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
        required   = True,
        label      = "Security Code",
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

            if not ((_digit & symbols and _upper & symbols) or \
                    (_digit & symbols and _lower & symbols) or \
                    (_lower & symbols and _upper & symbols)):
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

class ChangePasswordIfAuthForm(forms.Form):
    """Password change form for authenticated users. """

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

    def clean_password_new(self):
        """Make sure `password_new` isn't too easy to break. """
        cleaned_data = self.cleaned_data

        password_old = cleaned_data.get('password_old')
        password_new = cleaned_data.get('password_new')

        if CHECK_STRENGTH:
            if len(password_new) < MIN_PASSWORD_LEN:
                raise forms.ValidationError('Password must have at least %i characters.' % MIN_PASSWORD_LEN)

            symbols = set(password_new)

            if not ((_digit & symbols and _upper & symbols) or \
                    (_digit & symbols and _lower & symbols) or \
                    (_lower & symbols and _upper & symbols)):
                raise forms.ValidationError('Password is too week. Invent better one.')

        if password_old == password_new:
            raise forms.ValidationError("New password dosen't differ from the old one.")

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

class ChangePasswordNoAuthForm(ChangePasswordIfAuthForm):
    """Password change form for anonymous users. """

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

    def __init__(self, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)

        self.fields.keyOrder = [
            'username',
            'password_old',
            'password_new',
            'password_new_again',
            'captcha',
        ]

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

class UserProfileForm(forms.Form):
    """User profile form. """

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

    affiliation = forms.CharField(
        required  = True,
        label     = "Affiliation",
        help_text = "e.g. University of Nevada",
    )

    address = forms.CharField(
        required  = True,
        label     = "Address",
        help_text = "You can use Unicode character set.",
    )

    city = forms.CharField(
        required  = True,
        label     = "City",
        help_text = "You can use Unicode character set.",
    )

    postal_code = forms.CharField(
        required  = True,
        label     = "Postal Code",
        help_text = "",
    )

    country = forms.CharField(
        required  = True,
        label     = "Country",
        help_text = "Enter english country name.",
    )

    phone = forms.CharField(
        required  = True,
        label     = "Phone Number",
        help_text = "e.g. +48 123 456 789",
    )

    speaker = forms.ChoiceField(
        required  = True,
        label     = "Are you going to be a conference speaker?",
        help_text = "If you choose 'Yes', you will be able to upload your abstracts.",
        choices   = [
            (True, 'Yes'),
            (False, 'No'),
        ],
        initial   = False,
    )

    student = forms.ChoiceField(
        required  = True,
        label     = "Are you a student participant?",
        help_text = "If you choose 'Yes', you will be required to provide a student ID.",
        choices   = [
            (True, 'Yes'),
            (False, 'No'),
        ],
        initial   = False,
    )

    accompanying = forms.IntegerField(
        required  = True,
        label     = "Number of accompanying persons",
        help_text = "",
        min_value = 0,
        initial   = 0,
    )

    vegeterian = forms.ChoiceField(
        required  = True,
        label     = "Do you require vegeterian food?",
        help_text = "",
        choices   = [
            (True, 'Yes'),
            (False, 'No'),
        ],
        initial   = False,
    )

    arrival = forms.DateTimeField(
        required  = True,
        label     = "Arrival Date",
        help_text = "e.g. 27/06/2010 17:30",
        input_formats = [
            '%d/%m/%Y %H:%M',      # '27/06/2010 17:30'
            '%d/%m/%Y, %H:%M',     # '27/06/2010, 17:30'
        ],
    )
    departure = forms.DateTimeField(
        required  = True,
        label     = "Departure Date",
        help_text = "e.g. 3/07/2010 8:00",
        input_formats = [
            '%d/%m/%Y %H:%M',      # '27/06/2010 17:30'
            '%d/%m/%Y, %H:%M',     # '27/06/2010, 17:30'
        ],
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

