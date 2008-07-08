# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.views.generic import list_detail
from django.contrib.comments.models import FreeComment
from cargo import settings
from cargo.djangobook.feeds import LatestNews
from cargo.djangobook.models import Claims, News

feeds = {
    'latest': LatestNews,
}

# передача данных в шаблон, неименованная функция необходима
# для вычисления значения при каждом вызове URL
news_info_extra = {
    'spelling_error_count': lambda: Claims.objects.count()
}

news_info = {
    'queryset': News.objects.order_by('-datetime')[:5],
    'template_name': 'news_list.html',
    'extra_context': news_info_extra # дополнительный контекст
}

urlpatterns = patterns('',
    # RSS
    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed',
     {'feed_dict': feeds}),

    (r'^$', 'cargo.djangobook.views.show_db_page'),
    (r'^index\.html$', 'cargo.djangobook.views.show_db_page'),
    (r'^ch(\d+)s?(\d+)?\.html$', 'cargo.djangobook.views.show_db_page'),
    (r'^(ap)([a-z])\.html$', 'cargo.djangobook.views.show_db_page'),
    
    # Новости DjangoBook, словарь news_info определён в начале файла
    (r'^news/', list_detail.object_list, news_info),

    # Система комментирования
    (r'^comments/', include('django.contrib.comments.urls.comments')),

    # Пользователи сообщают об ошибках
    (r'^claim/', 'cargo.djangobook.views.user_claims'),

)
