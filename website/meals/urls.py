from django.conf.urls import url
from . import views

app_name = 'meals'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^wall/$', views.wall, name='wall'),
    url(r'^account/$', views.account, name='account'),
    url(r'^registration/$', views.registration, name='registration'),
    url(r'^login/$', views.login, name='login')
]
