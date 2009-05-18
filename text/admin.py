# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from text.models import Text

class TextAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Параметры',
         {'fields': ('label', 'text')}),
        )
    list_display = ('label', 'text', 'reg_date')

admin.site.register(Text, TextAdmin)
