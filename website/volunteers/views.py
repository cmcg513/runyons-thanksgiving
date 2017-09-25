from django.shortcuts import render, redirect
from . import forms
from website.settings import RECAPTCHA_URL, RECAPTCHA_PUBLIC_KEY
from website.local_settings import RECAPTCHA_PRIVATE_KEY
import requests
import json

def index(request):
    return redirect('volunteers:about', permanent=True)

def about(request):
    return render(request, 'volunteers/about.html', {})

def contact(request):
    error_message='Failed to validate CAPTCHA. Please make sure you check the box below'
    if request.method == 'POST':
        # print(request.POST)
        form = forms.ContactForm(request.POST)
        if form.is_valid():
            # import IPython; IPython.embed()
            # print(request.POST)
            payload = {
                'secret': RECAPTCHA_PRIVATE_KEY,
                'response': request.POST['g-recaptcha-response']
            }
            ip = _get_client_ip(request)
            if ip is not None:
                payload['remoteip'] = ip
            resp = requests.post(RECAPTCHA_URL, data=payload)
            if _successful_captcha(resp):
                return redirect('volunteers:thanks')
    else:
        form = forms.ContactForm()
    return render(request, 'volunteers/contact.html', {'form': form, 'error_message': error_message})

def thanks(request):
    return render(request, 'volunteers/thanks.html', {})


# https://stackoverflow.com/questions/4581789/how-do-i-get-user-ip-address-in-django
def _get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for is not None:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def _successful_captcha(response):
    if response.status_code == 200:
        content = json.loads(response.content)
        return content['success']
    return False
