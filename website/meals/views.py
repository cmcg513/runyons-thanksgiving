from django.shortcuts import render, redirect
from . import forms
from website.settings import \
    RECAPTCHA_PUBLIC_KEY, \
    NO_MORE_CLIENTS, \
    CLIENT_REGISTRATION_FORTHCOMING, \
    CLIENT_REGISTRATION_START_DATE
from website.shared import utils


def index(request):
    """
    Redirects to view for the password wall for registration
    """
    if 'wall_validated' in request.session and request.session['wall_validated']:
        return redirect('meals:account')
    else:
        return redirect('meals:wall')


def wall(request):
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
                    # set session var and redirect to registration on success
                    request.session['wall_validated'] = True
                    return redirect('meals:account')
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
            'meals/wall.html',
            {
                'form': form,
                'RECAPTCHA_PUBLIC_KEY': RECAPTCHA_PUBLIC_KEY,
                'error_message': error_message,
                'resubmit': resubmit,
                'CLIENT_REGISTRATION_FORTHCOMING': CLIENT_REGISTRATION_FORTHCOMING,
                'CLIENT_REGISTRATION_START_DATE': CLIENT_REGISTRATION_START_DATE
            }
        )


def account(request):
    """
    View for registering new accounts
    """
    if 'wall_validated' in request.session and request.session['wall_validated']:
        return render(request, 'meals/account.html')
    else:
        return redirect('meals:wall')


def registration(request):
    """
    View for registering meal recipients
    """
    return render(request, 'meals/registration.html')
