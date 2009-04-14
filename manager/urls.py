# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'moiluchru.manager.views.login'),
    (r'^logout', 'moiluchru.manager.views.logout'),
    (r'^orders/(?P<act>[a-z]+)/(?P<page>\d+)/', 'moiluchru.manager.views.orders'),
    (r'^orders/(?P<act>[a-z]+)/', 'moiluchru.manager.views.orders'),
    (r'^orderinfo/(?P<order_id>\d+)/', 'moiluchru.manager.views.order_info'),
    (r'^error/', 'moiluchru.manager.views.error'),
)
