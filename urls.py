# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.contrib import admin

#автоматическое подключение необходимых приложений
admin.autodiscover()

urlpatterns = patterns(
    '',
    # Интерфейс администратора
    (r'^admin/(.*)', admin.site.root),
    
    # Управление авторизацией пользователей
    (r'^accounts/login', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout',
     {'next_page': '/accounts/login/'}),
    
    (r'^$', 'django.views.generic.simple.redirect_to', {'url': '/shop/'}),
    (r'^shop/', include('moiluchru.shop.urls')),
)
