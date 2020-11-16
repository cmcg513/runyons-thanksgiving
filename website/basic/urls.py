from django.conf.urls import url
from website.donations import views as donationsviews
from . import views
from website.settings import DONE_FOR_THE_YEAR, COVID_19

urlpatterns = []

app_name = 'basic'
if DONE_FOR_THE_YEAR:
    urlpatterns.append(url(r'^.*$', views.index, name='index'))
elif COVID_19:
    urlpatterns.append(url(r'^donations/$', donationsviews.index, name='donations'))
    urlpatterns.append(url(r'^.*$', views.index, name='index'))
else:
    urlpatterns.append(url(r'^$', views.index, name='index'))

