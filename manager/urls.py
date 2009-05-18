# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'manager.views.login'),
    (r'^logout', 'manager.views.logout'),
    (r'^orders/(?P<act>[a-z]+)/(?P<page>\d+)/', 'manager.views.orders'),
    (r'^orders/(?P<act>[a-z]+)/', 'manager.views.orders'),
    (r'^orderinfo/(?P<order_id>\d+)/', 'manager.views.order_info'),
    (r'^error/', 'manager.views.error'),
)
