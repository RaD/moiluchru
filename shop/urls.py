# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'moiluchru.shop.views.show_main_page'),
    # страница результатов поиска может иметь продолжение (paginator)
    (r'^search/(?P<page>\d+)/', 'moiluchru.shop.views.search_results'),
    (r'^search/', 'moiluchru.shop.views.search_results'),
    # сортировка
    (r'^sort/(?P<mode>\d)/', 'moiluchru.shop.views.set_sort_mode'),
    # производитель
    (r'^producer/(?P<producer_id>\d+)/(?P<category_id>\d+)/(?P<page>\d+)/', 'moiluchru.shop.views.show_producer_page'),
    (r'^producer/(?P<producer_id>\d+)/(?P<category_id>\d+)/', 'moiluchru.shop.views.show_producer_page'),
    (r'^producer/(?P<producer_id>\d+)/', 'moiluchru.shop.views.show_producer_page'),

    # AJAX
    (r'^add', 'moiluchru.shop.ajax.add_to_cart'),
    (r'^clean', 'moiluchru.shop.ajax.clean_cart'),
                       
)

