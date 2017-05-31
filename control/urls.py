from django.conf.urls import include, url

from control import views

app_name = 'control'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^switch/$', views.switch),
    url(r'^switch/temp$', views.switch_temp),
    url(r'^events/latest/$', views.getLatestControlEvent),
    url(r'^status/$', views.status),
    url(r'^status/temp/$', views.status_temp),
]
