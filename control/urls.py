from django.conf.urls import patterns, include, url

from control import views

urlpatterns = patterns('',
    url(r'^$', views.index),
    url(r'^switch/$', views.switch),
    url(r'^switch/temp$', views.switch_temp),
    url(r'^events/latest/$', views.getLatestControlEvent),
    url(r'^status/$', views.status),
    url(r'^status/temp/$', views.status_temp),
)
