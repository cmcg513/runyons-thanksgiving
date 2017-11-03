from django.shortcuts import render
from website.settings import DONATIONS_CSV_PATH
import csv


def index(request):
    """
    Primary view for the Donations page
    """
    donations = []
    try:
        with open(DONATIONS_CSV_PATH, 'r') as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                if len(row) != 3:
                    continue
                donations.append(row)
    except (csv.Error, FileNotFoundError):
        pass

    if len(donations) == 0:
        error_msg = "Unfortunately, it looks like something went wrong loading the list of items... " \
                    "Check back with us later :)"
    else:
        error_msg = None

    return render(request, 'donations/index.html', {'donations': donations, 'error_msg': error_msg})
