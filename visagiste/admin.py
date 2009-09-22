# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib import admin
from django import forms
from django.utils.translation import ugettext_lazy as _

from visagiste import models

class TemplateAdmin(admin.ModelAdmin):
    fieldsets = ((None, {'fields': ('name', 'content')}),)
    list_display = ('name','last_modification')
    ordering = ('name',)

admin.site.register(models.Template, TemplateAdmin)
