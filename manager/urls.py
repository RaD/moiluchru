# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'manager.views.login', name='index'),
    url(r'^logout', 'manager.views.logout'),
    url(r'^orders/(?P<act>[a-z]+)(/(?P<page>\d+))?/$', 'manager.views.orders', name='orders'),
    url(r'^orderinfo/(?P<order_id>\d+)/', 'manager.views.order_info', name='orderinfo'),
    url(r'^error/', 'manager.views.error'),
)
