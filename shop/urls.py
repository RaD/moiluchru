# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'shop.views.show_main_page'),
    # сортировка
    (r'^sort/(?P<mode>\d)/', 'shop.views.set_sort_mode'),
    # производитель
#     (r'^producer/(?P<producer_id>\d+)/(?P<category_id>\d+)/(?P<page>\d+)/', 'shop.views.show_producer_page'),
#     (r'^producer/(?P<producer_id>\d+)/(?P<category_id>\d+)/', 'shop.views.show_producer_page'),
#     (r'^producer/(?P<producer_id>\d+)/', 'shop.views.show_producer_page'),

    # AJAX
    (r'^clean', 'shop.ajax.clean_cart'),
                       
)

