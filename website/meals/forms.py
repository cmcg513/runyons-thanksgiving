from django import forms
from django.core.exceptions import ValidationError
from website.settings import SHARED_PASSWORD


def validate_password(password):
    if str(password) != str(SHARED_PASSWORD):
        raise ValidationError("Invalid password")


class MealRegistrationForm(forms.Form):

    password = forms.CharField(
        required=True,
        validators=[validate_password]
    )



