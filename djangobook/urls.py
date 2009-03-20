# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from cargo import settings
from cargo.djangobook.feeds import LatestNews

feeds = { 'latest': LatestNews, }

urlpatterns = patterns('',
    # RSS
    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),

    (r'^$', 'cargo.djangobook.views.show_db_page'),
    (r'^index\.html$', 'cargo.djangobook.views.show_db_page'),
    (r'^ch(\d+)s?(\d+)?\.html$', 'cargo.djangobook.views.show_db_page'),
    (r'^(ap)([a-z])\.html$', 'cargo.djangobook.views.show_db_page'),
    (r'^news/?(?P<news_id>\d+)?/$', 'cargo.djangobook.views.show_news_page'),
    (r'^archive/$', 'cargo.djangobook.views.show_archive_page'),
    (r'^archive/(?P<year>\d{4})/$', 'cargo.djangobook.views.show_archive_page'),
    (r'^archive/(?P<year>\d{4})/(?P<month>\d+)/$', 'cargo.djangobook.views.show_archive_page'),
    (r'^text/?(?P<label>\w+)?/$', 'cargo.djangobook.views.text'),
    
    (r'^search/', 'cargo.djangobook.views.search'),

    # Пользователи сообщают об ошибках
    (r'^claim/', 'cargo.djangobook.views.user_claims'),

    # ajax
    (r'^pending/', 'cargo.djangobook.views.claims_penging'),
    (r'^version/', 'cargo.djangobook.views.version'),
                       
)
