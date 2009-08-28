from django import forms

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from esco.settings import MIN_PASSWORD_LEN

class LoginForm(forms.Form):
    """Form for logging in users. """

    login = forms.EmailField(
        required = True,
        label    = "Login",
    )

    password = forms.CharField(
        required = True,
        label    = "Password",
        widget   = forms.PasswordInput(),
    )

    remember = forms.BooleanField(
        required = False,
        label    = "Remember Me",
        widget   = forms.CheckboxInput(),
    )

class ReminderForm(forms.Form):
    """Password reminder form. """

    login = forms.EmailField(
        required = True,
        label    = "Login",
    )

class RegistrationForm(forms.Form):
    """Form for creating new users. """

    _digit = set(map(chr, range(48, 58)))
    _upper = set(map(chr, range(65, 91)))
    _lower = set(map(chr, range(97,123)))

    username = forms.EmailField(
        required   = True,
        label      = "E-mail",
        help_text  = "This will be your login.",
    )
    username_again = forms.EmailField(
        required   = True,
        label      = "E-mail (Again)",
    )

    password = forms.CharField(
        required   = True,
        label      = "Password",
        min_length = MIN_PASSWORD_LEN,
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

    def clean_username(self):
        """Make sure `login` is unique in the system. """
        username = self.cleaned_data['username']

        try:
            User.objects.get(username=username)
        except ObjectDoesNotExist:
            return username

        raise forms.ValidationError('Username is already in use.')

    def clean_username_again(self):
        """Make sure user verified `login` he entered. """
        if 'username' in self.cleaned_data:
            username       = self.cleaned_data['username']
            username_again = self.cleaned_data['username_again']

            if username == username_again:
                return username
        else:
            return None

        raise forms.ValidationError('Usernames do not match.')

    def clean_password1(self):
        """Make sure `password` isn't too easy to break. """
        password = self.cleaned_data['password']

        letters = set(password)

        if (not self._digit & letters) or \
           (not self._upper & letters) or \
           (not self._lower & letters):
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

