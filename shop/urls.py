# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.views.generic import list_detail
from cargo.shop.models import Category

urlpatterns = patterns('',
    (r'^$', 'cargo.shop.views.show_main_page'),
    (r'^category/(?P<category>\d+)/', 'cargo.shop.views.show_category_page'),
    (r'^item/(?P<item>\d+)/', 'cargo.shop.views.show_item_page'),
    (r'^add', 'cargo.shop.views.add_to_cart'),
    (r'^clean', 'cargo.shop.views.clean_cart'),
    (r'^count', 'cargo.shop.views.show_count'),
    (r'^cart', 'cargo.shop.views.show_cart'),
    (r'^offer', 'cargo.shop.views.show_offer'),
    (r'^ordered', 'cargo.shop.views.show_ordered'),
)

