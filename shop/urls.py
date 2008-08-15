# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.views.generic import list_detail
from cargo.shop.models import Category

urlpatterns = patterns('',
    (r'^$', 'cargo.shop.views.show_main_page'),
    (r'^howto/(?P<howto>\d+)/', 'cargo.shop.views.show_howto_page'),
    (r'^category/(?P<category>\d+)/(?P<page>\d+)/', 'cargo.shop.views.show_category_page'),
    (r'^category/(?P<category>\d+)/', 'cargo.shop.views.show_category_page'),
    (r'^producer/(?P<producer>\d+)/(?P<category>\d+)/(?P<page>\d+)/', 'cargo.shop.views.show_producer_page'),
    (r'^producer/(?P<producer>\d+)/(?P<category>\d+)/', 'cargo.shop.views.show_producer_page'),
    (r'^item/(?P<item>\d+)/', 'cargo.shop.views.show_item_page'),
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

