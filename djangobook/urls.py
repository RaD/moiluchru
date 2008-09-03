# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from cargo import settings
#from cargo.djangobook.feeds import LatestNews

#feeds = {
#    'latest': LatestNews,
#}

urlpatterns = patterns('',
    # RSS
    #(r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed',
    # {'feed_dict': feeds}),

    (r'^$', 'cargo.djangobook.views.show_db_page'),
    (r'^index\.html$', 'cargo.djangobook.views.show_db_page'),
    (r'^ch(\d+)s?(\d+)?\.html$', 'cargo.djangobook.views.show_db_page'),
    (r'^(ap)([a-z])\.html$', 'cargo.djangobook.views.show_db_page'),
    
    # Пользователи сообщают об ошибках
    (r'^claim/', 'cargo.djangobook.views.user_claims'),

)
