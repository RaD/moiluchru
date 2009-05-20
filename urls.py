# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

#автоматическое подключение необходимых приложений
from django.contrib import admin
admin.autodiscover()

handler404 = 'shop.views.handler404'
#handler500 = 'shop.views.handler500'

# карта сайта
from django.contrib.sitemaps import Sitemap, FlatPageSitemap, GenericSitemap
from shop.models import Item

sitemap_dict = {
    'queryset': Item.objects.all(),
    'date_field': 'reg_date',
}

sitemaps = {
    'flatpages': FlatPageSitemap,
    'items': GenericSitemap(sitemap_dict, priority=0.6),
}

class ItemSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.5

    def items(self):
        return Item.objects.filter(is_present=True)

    def lastmod(self, obj):
        return obj.last_modification

    def location(self, obj):
        return obj.get_absolute_url_by_title()

sitemaps = {
    'items': ItemSitemap(),
}

urlpatterns = patterns(
    '',
    # Интерфейс администратора
    (r'^admin/doc/', include('django.contrib.admindocs/urls')),
    (r'^admin/(.*)', admin.site.root),

    # карта сайта, robots.txt
    (r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    (r'^robots.txt$', include('robots.urls')),

    #(r'^$', 'django.views.generic.simple.redirect_to', {'url': '/shop/'}),
    (r'^$', 'shop.views.show_main_page'),

    # страница результатов поиска
    (r'^search/', 'shop.views.search_query'),
    (r'^result/((?P<page>\d+)/)?', 'shop.views.search_results'),
    (r'^tag/(?P<tag>\w+)/', 'shop.views.tag_results'),

    # список товаров
    (r'^items/((?P<page>\d+)/)?', 'shop.views.show_items'),

    # категории товаров
    (r'^category/(?P<category_id>\d+)/((?P<page>\d+)/)?', 
     'shop.views.show_category_page'),

    # коллекции товаров
    (r'^collection/(?P<collection_id>\d+)/((?P<page>\d+)/)?', 
     'shop.views.show_collection_page'),

    # товар
    (r'^item/(?P<item_id>\d+)/', 'shop.views.show_item_page'),
    (r'^item/(?P<item_title>\d+\-\d+\-\d+)/', 'shop.views.show_item_by_title_page'),

    # процесс покупки
    (r'^cart', 'shop.views.show_cart'),
    (r'^offer', 'shop.views.show_offer'),
    (r'^ordered', 'shop.views.show_ordered'),

    # отображение текстов
    (r'^text/((?P<label>\w+)/)?', 'shop.views.show_text_page'),

    # магазин
    (r'^shop/', include('shop.urls')),

    # интерфейс менеджера
    (r'^manager/', include('manager.urls')),

    # ajax
    (r'^ajax/cart/add', 'shop.ajax.add_to_cart'),
    (r'^ajax/cart/remove/', 'shop.ajax.cart_remove_item'),
    (r'^ajax/cart/recalculate/', 'shop.ajax.cart_recalculate'),
    (r'^ajax/jabber/message', 'shop.ajax.jabber_message'),
    (r'^ajax/jabber/poll', 'shop.ajax.jabber_poll'),
    
)
