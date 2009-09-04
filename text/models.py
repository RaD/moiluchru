# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.admin.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.flatpages.models import FlatPage

class ProxyFlatPageManager(models.Manager):
    def get_query_set(self):
        return FlatPage.objects.filter(url__regex=r'^\/article\/[^\/]+\/$')

class ArticleProxy(FlatPage):
    objects = ProxyFlatPageManager()

    class Meta:
        proxy = True
        verbose_name = _(u'Article')
        verbose_name_plural = _(u'Articles')
