from django.conf.urls import include, url

from django.contrib import admin
from django.contrib import auth
admin.autodiscover()

import templog.urls
import control.urls
from thermoctrl import views

urlpatterns = [
    # Examples:
    # url(r'^$', 'thermoctrl.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', views.index, name='index'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^log/', include(templog.urls), name='log'),
    url(r'^control/', include(control.urls), name='control'),
    url(r'^login/', auth.views.login, {"SSL": True, "template_name": "main/login.html"}, name='login'),
]
