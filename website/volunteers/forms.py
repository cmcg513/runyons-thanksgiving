from django import forms
from website.basic.forms import PhoneField

class ContactForm(forms.Form):
    name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    phone = PhoneField(required=True)
    number_of_adults = forms.IntegerField(required=True)
    number_of_children = forms.IntegerField(required=True)
    preference = forms.ChoiceField(
        required=True,
        choices=(
            ('driver','driver'),
            ('in_house','in house'),
            ('no_preference','no preference')
            )
        )
    details = forms.CharField(
        required=False,
        widget=forms.Textarea()
    )
