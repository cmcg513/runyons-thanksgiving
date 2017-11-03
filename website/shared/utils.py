from website.settings import SHEETS_API_KEY, SHEETS_API_SCOPE, GOOGLE_DISCOVERY_URL, SHEETS_INPUT_OPTION
from oauth2client.service_account import ServiceAccountCredentials
import httplib2
from apiclient import discovery
from datetime import datetime
import pytz
import json


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


def form_to_sheets_append_body(form, field_order, add_ts):
    """
    Parse the fields of a form object into a Sheets API compatible body, adding in a timestamp if requested
    """
    if add_ts:
        # get dt string
        dt = get_formatted_datetime()
        body = [dt]
    else:
        body = []

    # setup the values to append to the sheet
    for key in field_order:
        body.append(form.data[key])
    body = {'values': [body]}

    return body


def push_form_to_sheets(sheet_id, form, field_order, add_ts=True):
    """
    Append the data from a form to the Google Sheet specified by the given id
    """
    sheets = get_sheets_service()
    body = form_to_sheets_append_body(form, field_order, add_ts)

    # create and execute the API request
    request = sheets.values().append(
        spreadsheetId=sheet_id,
        body=body,
        range='A:A',
        valueInputOption=SHEETS_INPUT_OPTION
    )
    request.execute()


def pull_data_from_sheets(sheet_id):
    """
    Grab the data from the Google Sheet specified by the given id
    """
    sheets = get_sheets_service()
    request = sheets.values().get(spreadsheetId=sheet_id, range='Sheet1!A2:C')
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
