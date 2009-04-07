# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'moiluchru.shop.views.show_main_page'),
    # страница результатов поиска может иметь продолжение (paginator)
    (r'^search/(?P<page>\d+)/', 'moiluchru.shop.views.search_results'),
    (r'^search/', 'moiluchru.shop.views.search_results'),
    # информация
    (r'^howto/(?P<howto>\d+)/', 'moiluchru.shop.views.show_howto_page'),
    # категория
    (r'^category/(?P<category_id>\d+)/(?P<page>\d+)/', 'moiluchru.shop.views.show_category_page'),
    (r'^category/(?P<category_id>\d+)/', 'moiluchru.shop.views.show_category_page'),
    # сортировка
    (r'^sort/(?P<mode>\d)/', 'moiluchru.shop.views.set_sort_mode'),
    # производитель
    (r'^producer/(?P<producer_id>\d+)/(?P<category_id>\d+)/(?P<page>\d+)/', 'moiluchru.shop.views.show_producer_page'),
    (r'^producer/(?P<producer_id>\d+)/(?P<category_id>\d+)/', 'moiluchru.shop.views.show_producer_page'),
    (r'^producer/(?P<producer_id>\d+)/', 'moiluchru.shop.views.show_producer_page'),
    # товар
    (r'^item/(?P<item_id>\d+)/', 'moiluchru.shop.views.show_item_page'),
    # процесс покупки
    (r'^cart', 'moiluchru.shop.views.show_cart'),
    (r'^offer', 'moiluchru.shop.views.show_offer'),
    (r'^ordered', 'moiluchru.shop.views.show_ordered'),

    # AJAX
    (r'^add', 'moiluchru.shop.ajax.add_to_cart'),
    (r'^clean', 'moiluchru.shop.ajax.clean_cart'),
    (r'^count', 'moiluchru.shop.ajax.show_count'),
                       
    # раздел менеджера
    (r'^manager/', 'moiluchru.shop.manager.login'),
    (r'^logout', 'moiluchru.shop.manager.logout'),
    (r'^orders/(?P<act>[a-z]+)/(?P<page>\d+)/', 'moiluchru.shop.manager.orders'),
    (r'^orders/(?P<act>[a-z]+)/', 'moiluchru.shop.manager.orders'),
    (r'^orderinfo/(?P<order_id>\d+)/', 'moiluchru.shop.manager.order_info'),
                       
)

