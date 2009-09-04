# -*- coding: utf-8 -*-

import os

from django.conf import settings
from django.contrib import admin
from django.contrib.flatpages.models import FlatPage
from django.shortcuts import get_object_or_404
from django import forms
from django.utils.translation import ugettext_lazy as _

from snippets import translit
from text import models


class ArticleProxyForm(forms.ModelForm):
    class Meta:
        model = FlatPage

class ArticleProxyAdmin(admin.ModelAdmin):
    form = ArticleProxyForm
    fieldsets = ((None, {'fields': ('title','content')}),
                 (_(u'More'), {'fields': ('sites',)}),)
    list_display = ('title', 'url')

    def queryset(self, request):
        return super(ArticleProxyAdmin, self).queryset(request)
    #.filter(url__regex=r'^\/article\/[^\/]+\/$')

    def save_model(self, request, obj, form, change):
        title = request.POST['title']
        obj.url = '/article/%s/' % (translit(title),)
        obj.template_name = u'flatpage.html'
        obj.save()

admin.site.register(models.ArticleProxy, ArticleProxyAdmin)
