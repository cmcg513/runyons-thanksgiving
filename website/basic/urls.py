from django.conf.urls import url
from . import views
from website.settings import DONE_FOR_THE_YEAR

app_name = 'basic'
if DONE_FOR_THE_YEAR:
    regex_pattern = r'^.*$'
else:
    regex_pattern = r'^$'

urlpatterns = [
    url(regex_pattern, views.index, name='index')
]
