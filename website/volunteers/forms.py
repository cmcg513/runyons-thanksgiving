from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(required=True)
    email = forms.CharField(required=True)
    body = forms.CharField(
        required=True,
        widget=forms.Textarea
    )
