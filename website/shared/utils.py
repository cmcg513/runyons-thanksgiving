from website.settings import \
    RECAPTCHA_URL, SHEETS_API_KEY, SHEETS_API_SCOPE, GOOGLE_DISCOVERY_URL, SHEETS_INPUT_OPTION, RECAPTCHA_PRIVATE_KEY, \
    DEFAULT_SHEETS_RANGE
from oauth2client.service_account import ServiceAccountCredentials
import httplib2
from apiclient import discovery
from datetime import datetime
import pytz
import json
import requests


def chars_in_string(chars, s):
    """
    Returns true if any 1 char in chars appears in s
    """
    for c in chars:
        if c in s:
            return True
    return False


def captcha_is_valid(request):
    """
    Returns a boolean indicating whether the CAPTCHA was successful
    """
    payload = {
        'secret': RECAPTCHA_PRIVATE_KEY,
        'response': request.POST['g-recaptcha-response']
    }

    # add IP, if any could be found
    ip = get_client_ip(request)
    if ip is not None:
        payload['remoteip'] = ip

    # pass data to Google
        response = requests.post(RECAPTCHA_URL, data=payload)

    return successful_captcha(response)


def get_sheets_service():
    """
    Initializes an authenticated connection to the Google Sheets API
    """
    # authenticate
    credentials = ServiceAccountCredentials.from_json_keyfile_name(SHEETS_API_KEY, SHEETS_API_SCOPE)
    http = credentials.authorize(httplib2.Http())

    # grab sheets service
    service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=GOOGLE_DISCOVERY_URL)
    sheets = service.spreadsheets()

    return sheets


def get_formatted_datetime():
    """
    Returns the current date/time as formatted string (Eastern timezone)
    """
    # get the current time (Eastern)
    utc = pytz.timezone('UTC')
    eastern = pytz.timezone('US/Eastern')
    dt = utc.localize(datetime.now()).astimezone(eastern).strftime("%Y-%m-%d %H:%M:%S.%s")

    return dt


def form_to_sheets_append_body(field_order, add_ts, form=None, mock_form=None):
    """
    Parse the fields of a form object into a Sheets API compatible body, adding in a timestamp if requested
    """
    if form is None and mock_form is None:
        raise ValueError('Both form and mock_form can\'t be None')

    if add_ts:
        # get dt string
        dt = get_formatted_datetime()
        body = [dt]
    else:
        body = []

    # setup the values to append to the sheet
    if form:
        for key in field_order:
            body.append(form.data[key])
    elif mock_form:
        for key in field_order:
            body.append(mock_form[key])
    body = {'values': [body]}

    return body


def push_form_to_sheets(sheet_id, field_order, form=None, mock_form=None, add_ts=True, range_=DEFAULT_SHEETS_RANGE):
    """
    Append the data from a form to the Google Sheet specified by the given id
    """
    sheets = get_sheets_service()
    body = form_to_sheets_append_body(field_order, add_ts, form=form, mock_form=mock_form)

    # create and execute the API request
    request = sheets.values().append(
        spreadsheetId=sheet_id,
        body=body,
        range=range_,
        valueInputOption=SHEETS_INPUT_OPTION
    )
    request.execute()


def pull_data_from_sheets(sheet_id, range_='Sheet1!A2:C'):
    """
    Grab the data from the Google Sheet specified by the given id
    """
    sheets = get_sheets_service()
    request = sheets.values().get(spreadsheetId=sheet_id, range=range_)
    response = request.execute()

    return response['values']


def successful_captcha(response):
    """
    Given an HTTP response from Google, it checks if the CAPTCHA was validated
    successfully
    """
    if response.status_code == 200:
        content = json.loads(response.content.decode('utf-8'))
        return content['success']
    return False


def get_client_ip(request):
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
