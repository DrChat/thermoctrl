from django.conf.urls import patterns, include, url

from templog import views

urlpatterns = patterns('',
    url(r'^$', views.index),
    url(r'^data/curDay/$', views.getDataCurDay),
    url(r'^data/last24h/$', views.getDataLast24h),
)
