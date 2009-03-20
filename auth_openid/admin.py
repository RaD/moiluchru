# -*- coding: utf-8

from django.contrib import admin
from cargo.auth_openid.models import OpenID

class OpenIDAdmin(admin.ModelAdmin):
    list_display = ['user', 'url']

admin.site.register(OpenID, OpenIDAdmin)
