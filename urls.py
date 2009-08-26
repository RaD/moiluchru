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

    # интерфейс менеджера
    (r'^manager/', include('manager.urls')),

    # ajax
    (r'^ajax/cart/add/', 'shop.ajax.add_to_cart'),
    (r'^ajax/cart/remove/', 'shop.ajax.cart_remove_item'),
    (r'^ajax/cart/recalculate/', 'shop.ajax.cart_recalculate'),
    (r'^ajax/cart/clean/', 'shop.ajax.clean_cart'),
    (r'^ajax/jabber/message/', 'shop.ajax.jabber_message'),
    (r'^ajax/jabber/poll/', 'shop.ajax.jabber_poll'),
    (r'^ajax/advice/random/', 'advice.views.get_random_advice'),

    # основное
    (r'^$', 'django.views.generic.simple.redirect_to', {'url': '/category/popular/'}),
    (r'^category/(?P<title>[\w_]+)/((?P<page>\d+)/)?', 'views.category'),
    (r'^collection/(?P<id>\d+)/((?P<page>\d+)/)?', 'views.collection'),
    (r'^tag/(?P<tag>\w+)/', 'views.tag_search'),
    (r'^search/', 'views.search_query'),
    (r'^result/((?P<page>\d+)/)?', 'views.search_results'),
    (r'^item/(?P<id>\d+)/', 'views.item'),
    #(r'^item/(?P<title>\d+\-\d+\-\d+)/', 'views.item'),
    #(r'^item/(?P<title>[\w\d\-]+)/', 'views.item'),

    # сортировка
    (r'^sort/(?P<mode>\d)/', 'views.set_sort_mode'),

    # процесс покупки
    (r'^cart', 'views.show_cart'),
    (r'^order', 'views.show_order'),
    (r'^profit', 'views.show_profit'),

    # отображение текстов
    #(r'^text/((?P<label>\w+)/)?', 'shop.views.show_text_page'),   
)
