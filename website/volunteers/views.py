from django.shortcuts import render, redirect
from . import forms
from website.settings import RECAPTCHA_URL, RECAPTCHA_PUBLIC_KEY, RECAPTCHA_PRIVATE_KEY, DEBUG
import requests
import json

def index(request):
    """
    Redirects to view for the 'About' page
    """
    return redirect('volunteers:about', permanent=True)

def about(request):
    """
    View for the 'About' page
    """
    return render(request, 'volunteers/about.html', {})

def contact(request):
    """
    View for the 'Contact' page

    Returns a blank form on GET and accepts form data on POST
    """
    # default to no error messages
    error_message = None

    # handle POST
    if request.method == 'POST':
        if DEBUG:
            print(request.POST)

        # parse form data
        form = forms.ContactForm(request.POST)

        # validate form
        if form.is_valid():
            # import IPython; IPython.embed()
            # create payload to send to Google for CAPTCHA validation
            payload = {
                'secret': RECAPTCHA_PRIVATE_KEY,
                'response': request.POST['g-recaptcha-response']
            }

            # add IP, if any could be found
            ip = _get_client_ip(request)
            if ip is not None:
                payload['remoteip'] = ip

            # pass data to Google
            resp = requests.post(RECAPTCHA_URL, data=payload)

            # render 'Thanks' on success
            if _successful_captcha(resp):
                return redirect('volunteers:thanks')
            else:
                # else, pass on the error
                error_message = 'Failed to validate CAPTCHA. Please make sure you check the box below'
    # handle GET
    else:
        # init blank form
        form = forms.ContactForm()

    # render response
    return render(request, 'volunteers/contact.html', {'form': form, 'error_message': error_message})

def thanks(request):
    """
    View for the 'Thanks' page
    """
    return render(request, 'volunteers/thanks.html', {})

def _get_client_ip(request):
    """
    https://stackoverflow.com/questions/4581789/how-do-i-get-user-ip-address-in-django
    
    Attempts to grab the client IP from the request header

    Returns None if IP couldn't be found
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for is not None:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def _successful_captcha(response):
    """
    Given an HTTP response from Google, it checks if the CAPTCHA was validated 
    successfully
    """
    if response.status_code == 200:
        content = json.loads(response.content)
        return content['success']
    return False
