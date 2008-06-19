# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.views.generic import list_detail
from cargo.shop.models import Category

# за exclude спасибо ravli: filter(parent__isnull=True) не работает, надо проверить
#    'queryset': Categories.objects.exclude(parent__id__isnull=False)[:5],
cats_info = {
    'queryset': Category.objects.filter(parent__isnull=True)[:5],
    'template_name': 'shop-categories.html',
}

urlpatterns = patterns('',
    (r'^$', list_detail.object_list, cats_info),
    (r'^category/(?P<category>\d+)/', 'cargo.shop.views.subcats'),
    (r'^item/(?P<item>\d+)/', 'cargo.shop.views.showitem'),
)
