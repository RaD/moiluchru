# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'cargo.shop.views.show_main_page'),
    # страница результатов поиска может иметь продолжение (paginator)
    (r'^search/(?P<page>\d+)/', 'cargo.shop.views.search_results'),
    (r'^search/', 'cargo.shop.views.search_results'),
    # информация
    (r'^howto/(?P<howto>\d+)/', 'cargo.shop.views.show_howto_page'),
    # категория
    (r'^category/(?P<category_id>\d+)/(?P<page>\d+)/', 'cargo.shop.views.show_category_page'),
    (r'^category/(?P<category_id>\d+)/', 'cargo.shop.views.show_category_page'),
    # сортировка
    (r'^sort/(?P<mode>\d)/', 'cargo.shop.views.set_sort_mode'),
    # производитель
    (r'^producer/(?P<producer_id>\d+)/(?P<category_id>\d+)/(?P<page>\d+)/', 'cargo.shop.views.show_producer_page'),
    (r'^producer/(?P<producer_id>\d+)/(?P<category_id>\d+)/', 'cargo.shop.views.show_producer_page'),
    (r'^producer/(?P<producer_id>\d+)/', 'cargo.shop.views.show_producer_page'),
    # товар
    (r'^item/(?P<item_id>\d+)/', 'cargo.shop.views.show_item_page'),
    # процесс покупки
    (r'^cart', 'cargo.shop.views.show_cart'),
    (r'^offer', 'cargo.shop.views.show_offer'),
    (r'^ordered', 'cargo.shop.views.show_ordered'),

    # AJAX
    (r'^add', 'cargo.shop.ajax.add_to_cart'),
    (r'^clean', 'cargo.shop.ajax.clean_cart'),
    (r'^count', 'cargo.shop.ajax.show_count'),
                       
    # раздел менеджера
    (r'^manager/', 'cargo.shop.manager.login'),
    (r'^logout', 'cargo.shop.manager.logout'),
    (r'^orders/(?P<act>[a-z]+)/(?P<page>\d+)/', 'cargo.shop.manager.orders'),
    (r'^orders/(?P<act>[a-z]+)/', 'cargo.shop.manager.orders'),
    (r'^orderinfo/(?P<order_id>\d+)/', 'cargo.shop.manager.order_info'),
                       
)

