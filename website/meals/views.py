from django.shortcuts import render, redirect
from . import forms
from website.settings import \
    RECAPTCHA_PUBLIC_KEY, \
    NO_MORE_CLIENTS, \
    CLIENT_REGISTRATION_FORTHCOMING, \
    CLIENT_REGISTRATION_START_DATE
from website.shared import utils
import time
from website.settings import SHARED_PASSWORD
from django.contrib.auth.models import User


def index(request):
    """
    Redirects to view for the password wall for registration
    """
    if NO_MORE_CLIENTS:
        return render(request, 'meals/no_more_clients.html', {})
    elif 'wall_validated' in request.session and request.session['wall_validated']:
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
        captcha_error = None
        password_error = None

        # defaults to assuming this is a resubmit
        resubmit = True

        # handle POST
        if request.method == 'POST':
            # parse form data
            form = forms.AuthWallForm(request.POST)

            try:
                valid_captcha = utils.captcha_is_valid(request)
            except Exception:
                captcha_error = 'An unexpected error has occurred'
                valid_captcha = False

            if valid_captcha:
                # validate form
                if form.is_valid():
                    password = form.cleaned_data['password']
                    if valid_wall_password(password):
                        # set session var and redirect to registration on success
                        request.session['wall_validated'] = True
                        return redirect('meals:account')
                    else:
                        password_error = 'Invalid password'
            else:
                # else, pass on the error
                captcha_error = 'Failed to validate CAPTCHA. Please make sure you check the box above'
        # handle GET
        else:
            # init blank form
            form = forms.AuthWallForm()
            resubmit = False

        # render response
        return render(
            request,
            'meals/wall.html',
            {
                'form': form,
                'RECAPTCHA_PUBLIC_KEY': RECAPTCHA_PUBLIC_KEY,
                'captcha_error': captcha_error,
                'password_error': password_error,
                'resubmit': resubmit,
                'CLIENT_REGISTRATION_FORTHCOMING': CLIENT_REGISTRATION_FORTHCOMING,
                'CLIENT_REGISTRATION_START_DATE': CLIENT_REGISTRATION_START_DATE
            }
        )


def account(request):
    """
    View for registering new accounts
    """
    if NO_MORE_CLIENTS:
        return render(request, 'meals/no_more_clients.html', {})
    elif 'wall_validated' in request.session and request.session['wall_validated']:
        # default to no error messages
        captcha_error = None

        # defaults to assuming this is a resubmit
        resubmit = True

        # handle POST
        if request.method == 'POST':
            # parse form data
            form = forms.AccountSetupForm(request.POST)

            try:
                valid_captcha = utils.captcha_is_valid(request)
            except Exception:
                captcha_error = 'An unexpected error has occurred'
                valid_captcha = False

            if valid_captcha:
                # validate form
                if form.is_valid():
                    # create user, set session var and redirect to registration on success
                    create_user(form)
                    request.session['account_creation'] = int(time.time())
                    return redirect('meals:login')
            else:
                # else, pass on the error
                captcha_error = 'Failed to validate CAPTCHA. Please make sure you check the box above'
        # handle GET
        else:
            # init blank form
            form = forms.AccountSetupForm()
            resubmit = False

        return render(
            request,
            'meals/account.html',
            {
                'form': form,
                'RECAPTCHA_PUBLIC_KEY': RECAPTCHA_PUBLIC_KEY,
                'error_message': captcha_error,
                'resubmit': resubmit
            }
        )
    else:
        return redirect('meals:wall')


def registration(request):
    """
    View for registering meal recipients
    """
    return render(request, 'meals/registration.html')


def login(request):
    """
    View for logging in
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
            form = forms.LoginForm(request.POST)

            try:
                valid_captcha = utils.captcha_is_valid(request)
            except Exception:
                error_message = 'An unexpected error has occurred'
                valid_captcha = False

            if valid_captcha:
                # validate form
                if form.is_valid():
                    # set session var and redirect to registration on success
                    return redirect('meals:registration')
            else:
                # else, pass on the error
                error_message = 'Failed to validate CAPTCHA. Please make sure you check the box above'
        # handle GET
        else:
            # init blank form
            form = forms.LoginForm()
            resubmit = False

        recent_account_creation = False
        if 'account_creation' in request.session:
            account_creation = request.session['account_creation']
            if (int(time.time()) - account_creation) <= 5:
                recent_account_creation = True

        return render(
            request,
            'meals/login.html',
            {
                'form': form,
                'RECAPTCHA_PUBLIC_KEY': RECAPTCHA_PUBLIC_KEY,
                'error_message': error_message,
                'resubmit': resubmit,
                'recent_account_creation': recent_account_creation
            }
        )


def valid_wall_password(password):
    """
    Validates the shared auth-wall password
    """
    return str(password) == str(SHARED_PASSWORD)


def create_user(form):
    """
    Creates and saves a user from form data, and the associated Registrar model
    """
    user = User.objects.create_user(
        username=form.cleaned_data['email'],
        first_name=form.cleaned_data['first_name'],
        last_name=form.cleaned_data['last_name'],
        email=form.cleaned_data['email'],
        password=form.cleaned_data['password']
    )
    user.registrar.organization = form.cleaned_data['organization']
    user.registrar.save()
