from django.shortcuts import render, redirect
from . import forms
from website.settings import VOLUNTEER_SPREADSHEET_ID, RECAPTCHA_PUBLIC_KEY, NO_MORE_VOLUNTEERS
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
    if NO_MORE_VOLUNTEERS:
        return render(request, 'volunteers/no_more_volunteers.html', {})
    else:
        # default to no error messages
        error_message = None

        # defaults to assuming this is a resubmit
        resubmit = True

        # handle POST
        if request.method == 'POST':
            # parse form data
            form = forms.ContactForm(request.POST)

            try:
                valid_captcha = utils.captcha_is_valid(request)
            except Exception:
                error_message = 'An unexpected error has occurred'
                valid_captcha = False

            if valid_captcha:
                # validate form
                if form.is_valid():
                    utils.push_form_to_sheets(VOLUNTEER_SPREADSHEET_ID, key_order, form=form)
                    return redirect('volunteers:thanks')
            else:
                # else, pass on the error
                error_message = 'Failed to validate CAPTCHA. Please make sure you check the box above'

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
