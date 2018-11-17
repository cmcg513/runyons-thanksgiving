from django.shortcuts import render, redirect
from . import forms
from website.settings import \
    RECAPTCHA_PUBLIC_KEY, \
    NO_MORE_CLIENTS, \
    CLIENT_REGISTRATION_FORTHCOMING, \
    CLIENT_REGISTRATION_START_DATE, \
    OPEN_CLOSE_SPREADSHEET_ID, \
    OPEN_CLOSE_SPREADSHEET_RANGE, \
    OPEN_CLOSE_TRUE_VALUE, \
    OPEN_CLOSE_FALSE_VALUE
from website.shared import utils
import time
from website.settings import SHARED_PASSWORD, MEALS_SPREADSHEET_ID
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import PermissionDenied

key_order = [
    'user_organization',
    'user_first_name',
    'user_last_name',
    'user_phone',
    'user_email',
    'first_name',
    'last_name',
    'phone',
    'town',
    'zip_code',
    'address',
    'unit',
    'meal_count',
    'details'
]


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
    elif 'wall_validated' in request.session and request.session['wall_validated']:
        return redirect('meals:account')
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
    elif request.user.is_authenticated:
        return redirect('meals:registration')
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
        raise PermissionDenied


def registration(request):
    """
    View for registering meal recipients
    """
    if request.user.is_authenticated:
        if not registration_open():
            return render(request, 'meals/no_more_clients.html', {})
        else:
            # defaults to assuming this is a resubmit
            resubmit = True

            # handle POST
            if request.method == 'POST':
                # parse form data
                form = forms.RegistrationForm(request.POST)

                # validate form
                if form.is_valid():
                    # mock form and push data to spreadsheet
                    mock_form = join_form_and_user(form, request.user)
                    utils.push_form_to_sheets(MEALS_SPREADSHEET_ID, key_order, mock_form=mock_form)

                    # update registration_count
                    request.user.registrar.registration_count += 1
                    request.user.registrar.save()
                    request.session['registration_complete'] = int(time.time())
                    return redirect('meals:registration')

            # handle GET
            else:
                # init blank form
                form = forms.RegistrationForm()
                resubmit = False

            recent_registration = False
            if 'registration_complete' in request.session:
                registration_complete = request.session['registration_complete']
                if (int(time.time()) - registration_complete) <= 5:
                    recent_registration = True

            return render(
                request,
                'meals/registration.html',
                {
                    'form': form,
                    'resubmit': resubmit,
                    'recent_registration': recent_registration
                }
            )
    else:
        raise PermissionDenied


def login_view(request):
    """
    View for logging in
    """
    if NO_MORE_CLIENTS:
        return render(request, 'meals/no_more_clients.html', {})
    elif request.user.is_authenticated:
        return redirect('meals:registration')
    else:
        # default to no error messages
        captcha_error = None
        invalid_login = None

        # defaults to assuming this is a resubmit
        resubmit = True

        # handle POST
        if request.method == 'POST':
            # parse form data
            form = forms.LoginForm(request.POST)

            try:
                valid_captcha = utils.captcha_is_valid(request)
            except Exception:
                captcha_error = 'An unexpected error has occurred'
                valid_captcha = False

            if valid_captcha:
                # validate form
                if form.is_valid():
                    # authenticate, login and redirect
                    user = authenticate(username=form.cleaned_data['email'], password=form.cleaned_data['password'])
                    if user is not None:
                        login(request=request, user=user)
                        return redirect('meals:registration')
                    else:
                        invalid_login = True
            else:
                # else, pass on the error
                captcha_error = 'Failed to validate CAPTCHA. Please make sure you check the box above'
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

        recent_logout = False
        if 'logged_out' in request.session:
            logged_out = request.session['logged_out']
            if (int(time.time()) - logged_out) <= 5:
                recent_logout = True

        return render(
            request,
            'meals/login.html',
            {
                'form': form,
                'RECAPTCHA_PUBLIC_KEY': RECAPTCHA_PUBLIC_KEY,
                'error_message': captcha_error,
                'resubmit': resubmit,
                'recent_account_creation': recent_account_creation,
                'recent_logout': recent_logout,
                'invalid_login': invalid_login
            }
        )


def logout_view(request):
    """
    View for logging out
    """
    if request.user.is_authenticated:
        logout(request)
        request.session['logged_out'] = int(time.time())
        return redirect('meals:login')
    else:
        return redirect('meals:login')


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
    user.registrar.phone = form.cleaned_data['phone']
    user.registrar.save()


def join_form_and_user(form, user):
    """
    Given a registration form and user, creates a new mock form
    """
    mock_form = {}
    mock_form['user_organization'] = user.registrar.organization
    mock_form['user_first_name'] = user.first_name
    mock_form['user_last_name'] = user.last_name
    mock_form['user_phone'] = user.registrar.phone
    mock_form['user_email'] = user.email
    mock_form['first_name'] = form.data['first_name']
    mock_form['last_name'] = form.data['last_name']
    mock_form['phone'] = form.data['phone']
    mock_form['town'] = form.data['town']
    mock_form['zip_code'] = form.data['zip_code']
    mock_form['address'] = form.data['address']
    mock_form['unit'] = form.data['unit']
    mock_form['meal_count'] = form.data['meal_count']
    mock_form['details'] = form.data['details']
    return mock_form


def registration_open():
    """
    Check if registration page should be closed
    """
    # local setting has highest priortiy
    if NO_MORE_CLIENTS:
        return False
    else:
        return sheet_says_open()


def sheet_says_open():
    """
    Check spreadsheet to see if registration should be closed
    """
    try:
        data = utils.pull_data_from_sheets(OPEN_CLOSE_SPREADSHEET_ID, range_=OPEN_CLOSE_SPREADSHEET_RANGE)
        yes_no = str(data[0][0])
        if yes_no == OPEN_CLOSE_TRUE_VALUE:
            return True
        elif yes_no == OPEN_CLOSE_FALSE_VALUE:
            return False
        else:
            raise ValueError('Invalid value in spreadsheet')
    except Exception:
        # fail open
        return True


