from django.shortcuts import render, redirect
from . import forms
from website.settings import RECAPTCHA_URL, RECAPTCHA_PRIVATE_KEY, DEBUG, VOLUNTEER_SPREADSHEET_ID, RECAPTCHA_PUBLIC_KEY
import requests
from website.shared import utils

key_order = [
    'name',
    'email',
    'phone',
    'number_of_adults',
    'number_of_children',
    'preference',
    'details'
]


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

    # defaults to assuming this is a resubmit
    resubmit = True

    # handle POST
    if request.method == 'POST':
        if DEBUG:
            print(request.POST)

        # parse form data
        form = forms.ContactForm(request.POST)

        print(form)

        # validate form
        if form.is_valid():
            # import IPython; IPython.embed()
            # create payload to send to Google for CAPTCHA validation
            payload = {
                'secret': RECAPTCHA_PRIVATE_KEY,
                'response': request.POST['g-recaptcha-response']
            }

            # add IP, if any could be found
            ip = utils.get_client_ip(request)
            if ip is not None:
                payload['remoteip'] = ip

            # pass data to Google
            resp = requests.post(RECAPTCHA_URL, data=payload)

            # render 'Thanks' on success
            if utils.successful_captcha(resp):
                try:
                    utils.push_form_to_sheets(VOLUNTEER_SPREADSHEET_ID, form, key_order)
                    return redirect('volunteers:thanks')
                except Exception:
                    error_message = 'An unexpected error has occurred'
            else:
                # else, pass on the error
                error_message = 'Failed to validate CAPTCHA. Please make sure you check the box below'
    # handle GET
    else:
        # init blank form
        form = forms.ContactForm()
        resubmit = False

    # render response
    return render(
        request,
        'volunteers/contact.html',
        {
            'form': form,
            'RECAPTCHA_PUBLIC_KEY': RECAPTCHA_PUBLIC_KEY,
            'error_message': error_message,
            'resubmit': resubmit
        }
    )


def thanks(request):
    """
    View for the 'Thanks' page
    """
    return render(request, 'volunteers/thanks.html', {})
