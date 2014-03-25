from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    #login
    url(r'^login/','precoinr.apps.auth.views.login_user'),
    url(r'^logout/','precoinr.apps.auth.views.logout_user'),

    #accounts
    url(r'^account/', include('precoinr.apps.AccountManager.urls')),

    #admin:
    url(r'^admin/', include(admin.site.urls)),
)
