from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import templog.urls
import control.urls
from thermoctrl import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'thermoctrl.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', 'thermoctrl.views.index', name='index'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^log/', include(templog.urls), name='log'),
    url(r'^control/', include(control.urls), name='control'),
    url(r'^login/', 'django.contrib.auth.views.login', {"SSL": True, "template_name": "main/login.html"}, name='login'),
)
