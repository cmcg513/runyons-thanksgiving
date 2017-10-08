from django.shortcuts import render, redirect
from . import forms
from website.settings import RECAPTCHA_URL, RECAPTCHA_PUBLIC_KEY, RECAPTCHA_PRIVATE_KEY, DEBUG, SHEETS_INPUT_OPTION, VOLUNTEER_API_KEY, SHEETS_API_SCOPE, GOOGLE_DISCOVERY_URL, VOLUNTEER_SPREADSHEET_ID
import requests
import json
from datetime import datetime
import pytz
from oauth2client.service_account import ServiceAccountCredentials
import httplib2
from apiclient import discovery

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
            ip = _get_client_ip(request)
            if ip is not None:
                payload['remoteip'] = ip

            # pass data to Google
            resp = requests.post(RECAPTCHA_URL, data=payload)

            # render 'Thanks' on success
            if _successful_captcha(resp):
                try:
                    _push_to_sheets(form)
                    return redirect('volunteers:thanks')
                except:
                    error_message='An unexpected error has occurred'
            else:
                # else, pass on the error
                error_message = 'Failed to validate CAPTCHA. Please make sure you check the box below'
    # handle GET
    else:
        # init blank form
        form = forms.ContactForm()
        resubmit = False

    # render response
    return render(request, 'volunteers/contact.html', {'form': form, 'error_message': error_message, 'resubmit': resubmit})

def thanks(request):
    """
    View for the 'Thanks' page
    """
    return render(request, 'volunteers/thanks.html', {})

def _push_to_sheets(form):
    # import IPython; IPython.embed()
    credentials = ServiceAccountCredentials.from_json_keyfile_name(VOLUNTEER_API_KEY, SHEETS_API_SCOPE)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=GOOGLE_DISCOVERY_URL)
    sheets = service.spreadsheets()
    utc = pytz.timezone('UTC')
    eastern = pytz.timezone('US/Eastern')
    dt = utc.localize(datetime.now()).astimezone(eastern).strftime("%Y-%m-%d %H:%M:%S.%s")
    body = [dt]
    for key in key_order:
        body.append(form.data[key])
    body = {'values':[body]}
    request = sheets.values().append(spreadsheetId=VOLUNTEER_SPREADSHEET_ID, body=body, range='A:A', valueInputOption=SHEETS_INPUT_OPTION)
    request.execute()

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
        content = json.loads(response.content.decode('utf-8'))
        return content['success']
    return False
