from django.conf.urls import patterns, url
from precoinr.apps.AccountManager import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^history/$', views.history, name='history'),
                       url(r'^create/$', views.create, name='create'))
