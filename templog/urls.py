from django.conf.urls import include, url

from templog import views

app_name = 'templog'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^data/last/(?P<hours>\d+)h/$', views.getDataLastHrs),

    # png/last/#...h/
    url(r'^png/last/(?P<hours>\d+)h/$', views.pngLastHrs),

    # pgf/last/#...h/
    url(r'^pgf/last/(?P<hours>\d+)h/$', views.pgfLastHrs),
]
