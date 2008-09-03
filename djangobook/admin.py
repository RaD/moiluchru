# -*- coding: utf-8 -*-

from django.contrib import admin
from cargo.djangobook.models import News, Claims

class NewsAdmin(admin.ModelAdmin):
    fieldsets = (
        (None,{'fields': ('title', 'datetime')}),
        ('Содержимое', {'fields': ('text',)}))
    list_display = ('title', 'datetime')
    ordered = ('-datetime')
admin.site.register(News, NewsAdmin)

class ClaimsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Мета', {'fields': ('datetime', 'url')}),
        ('Ошибка', {'fields': ('ctx_left', 'selected', 'ctx_right')}),
        ('Комментарий', {'fields': ('email','comment')}))
    list_display = ('email', 'comment', 'url', 'datetime')
    ordered = ('-datetime')
admin.site.register(Claims, ClaimsAdmin)
