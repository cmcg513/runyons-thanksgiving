from django.shortcuts import render, redirect
from . import forms
from website.settings import CLIENT_REGISTRATION_URL, RECAPTCHA_PUBLIC_KEY, NO_MORE_CLIENTS
from website.shared import utils



def index(request):
    """
    Primary view for the Meals page
    """
    if NO_MORE_CLIENTS:
        return render(request, 'meals/no_more_clients.html', {})
    else:
        # default to no error messages
        error_message = None

        # defaults to assuming this is a resubmit
        resubmit = True

        # handle POST
        if request.method == 'POST':
            # parse form data
            form = forms.MealRegistrationForm(request.POST)

            try:
                valid_captcha = utils.captcha_is_valid(request)
            except Exception:
                error_message = 'An unexpected error has occurred'
                valid_captcha = False

            if valid_captcha:
                # validate form
                if form.is_valid():
                    # redirect to Google Form on success
                    return redirect(CLIENT_REGISTRATION_URL)
            else:
                # else, pass on the error
                error_message = 'Failed to validate CAPTCHA. Please make sure you check the box above'
        # handle GET
        else:
            # init blank form
            form = forms.MealRegistrationForm()
            resubmit = False

        # render response
        return render(
            request,
            'meals/index.html',
            {
                'form': form,
                'RECAPTCHA_PUBLIC_KEY': RECAPTCHA_PUBLIC_KEY,
                'error_message': error_message,
                'resubmit': resubmit
            }
        )
