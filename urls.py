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

    # магазин
    (r'^shop/', include('moiluchru.shop.urls')),

    # отображение текстов
    (r'^text/((?P<label>\w+)/)?', 'moiluchru.shop.views.show_text_page'),

    # интерфейс менеджера
    (r'^manager/', include('moiluchru.manager.urls')),
)
