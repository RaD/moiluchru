# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

#автоматическое подключение необходимых приложений
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    # Интерфейс администратора
    (r'^admin/doc/', include('django.contrib.admindocs/urls')),
    (r'^admin/(.*)', admin.site.root),

    (r'^$', 'django.views.generic.simple.redirect_to', {'url': '/shop/'}),
    (r'^shop/', include('moiluchru.shop.urls')),
)
