from django import forms
from website.basic.forms import PhoneField

class ContactForm(forms.Form):
    name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    phone = PhoneField(required=True)
    number_of_adults = forms.IntegerField(required=True)
    number_of_children = forms.IntegerField(required=True)
    preference = forms.CharField(
        required=True,
        widget=forms.Select(choices=(
            ('in_house','in house'),
            ('driver','driver'),
            ('either','either')
            ))
        )
    body = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'rows': '5', 'cols': '50'})
    )
