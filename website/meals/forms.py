from django import forms
from django.core.exceptions import ValidationError
from website.basic.forms import PhoneField
import string
from website.shared import utils
import django.contrib.auth.password_validation


def validate_password(password):
    """
    Validates password complexity
    """
    if not utils.chars_in_string(string.ascii_lowercase, password):
        raise ValidationError('Password must contain lowercase characters')
    elif not utils.chars_in_string(string.ascii_uppercase, password):
        raise ValidationError('Password must contain uppercase characters')
    elif not utils.chars_in_string(string.digits, password):
        raise ValidationError('Password must contain numbers')
    elif not utils.chars_in_string(string.punctuation, password):
        raise ValidationError('Password must contain a symbol')


class AuthWallForm(forms.Form):
    """
    Simple form for the password wall for user account setup
    """
    password = forms.CharField(required=True)


class AccountSetupForm(forms.Form):
    """
    Form for setting up user accounts for meal registration
    """
    organization = forms.CharField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    phone = PhoneField(required=True)
    password = forms.CharField(
        required=True,
        validators=[django.contrib.auth.password_validation.validate_password, validate_password]
    )
    password_confirmation = forms.CharField(required=True)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirmation = cleaned_data.get('password_confirmation')

        if password != password_confirmation:
            msg = 'Passwords do not match'
            self.add_error('password_confirmation', msg)


class LoginForm(forms.Form):
    """
    Login form
    """
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True)
