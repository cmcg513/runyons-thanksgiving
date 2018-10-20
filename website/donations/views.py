from django.shortcuts import render
from website.settings import DONATIONS_SPREADSHEET_ID, WAIT_BEFORE_DONATING, DONATE_START_DATE
from website.shared import utils


def index(request):
    """
    Primary view for the Donations page
    """
    donations = []
    try:
        data = utils.pull_data_from_sheets(DONATIONS_SPREADSHEET_ID)
        for row in data:
            if len(row) == 0:
                continue
            elif len(row) < 3:
                while len(row) < 3:
                    row.append('')
            elif len(row) > 3:
                raise ValueError('Too many values!')
            donations.append(row)
    except Exception:
        pass

    if len(donations) == 0:
        error_msg = "Unfortunately, it looks like something went wrong loading the list of items... " \
                    "Check back with us later :)"
    else:
        error_msg = None

    return render(request, 'donations/index.html', {
        'donations': donations,
        'error_msg': error_msg,
        'WAIT_BEFORE_DONATING': WAIT_BEFORE_DONATING,
        'DONATE_START_DATE': DONATE_START_DATE
    })
