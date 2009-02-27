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
    
    # Подключение схем URL
    (r'^openid/$', 'cargo.openidconsumer.views.begin'),
    (r'^openid/complete/$', 'cargo.openidconsumer.views.complete'),
    (r'^openid/signout/$', 'cargo.openidconsumer.views.signout'),
    (r'^djangobook/', include('cargo.djangobook.urls')),
    (r'^shop/', include('cargo.shop.urls')),
)
