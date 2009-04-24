# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

#автоматическое подключение необходимых приложений
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    # Интерфейс администратора
    (r'^admin/doc/', include('django.contrib.admindocs/urls')),
    (r'^admin/(.*)', admin.site.root),

    #(r'^$', 'django.views.generic.simple.redirect_to', {'url': '/shop/'}),
    (r'^$', 'moiluchru.shop.views.show_main_page'),

    # страница результатов поиска
    (r'^search/', 'moiluchru.shop.views.search_query'),
    (r'^result/((?P<page>\d+)/)?', 'moiluchru.shop.views.search_results'),
    (r'^tag/(?P<tag>\w+)/', 'moiluchru.shop.views.tag_results'),

    # список товаров
    (r'^items/((?P<page>\d+)/)?', 
     'moiluchru.shop.views.show_items'),

    # категории товаров
    (r'^category/(?P<category_id>\d+)/((?P<page>\d+)/)?', 
     'moiluchru.shop.views.show_category_page'),

    # товар
    (r'^item/(?P<item_id>\d+)/', 'moiluchru.shop.views.show_item_page'),

    # процесс покупки
    (r'^cart', 'moiluchru.shop.views.show_cart'),
    (r'^offer', 'moiluchru.shop.views.show_offer'),
    (r'^ordered', 'moiluchru.shop.views.show_ordered'),

    # отображение текстов
    (r'^text/((?P<label>\w+)/)?', 'moiluchru.shop.views.show_text_page'),

    # магазин
    (r'^shop/', include('moiluchru.shop.urls')),

    # интерфейс менеджера
    (r'^manager/', include('moiluchru.manager.urls')),

    # ajax
    (r'^ajax/cart/add', 'moiluchru.shop.ajax.add_to_cart'),
    (r'^ajax/cart/remove/', 'moiluchru.shop.ajax.cart_remove_item'),
    (r'^ajax/cart/recalculate/', 'moiluchru.shop.ajax.cart_recalculate'),
)
