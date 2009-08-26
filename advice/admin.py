# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from advice.models import Text

class TextAdmin(admin.ModelAdmin):
    fieldsets = ((_(u'Main'), 
                  {'fields': (('weight'),
                              ('enabled'),
                              ('title'), 
                              ('desc'))}),
                 )
    list_display = ('title', 'weight', 'enabled')
    ordering = ('weight', 'title')
admin.site.register(Text, TextAdmin)
