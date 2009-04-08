# -*- coding: utf-8 -*-

from django.contrib import admin
from moiluchru.shop.models import Color, Country, Producer, Category, Item, Buyer, Order

class ColorAdmin(admin.ModelAdmin):
    fieldsets = ((None,{'fields': ('title',)}),)
    list_display = ('title',)
    ordered = ('title',)

class CountryAdmin(admin.ModelAdmin):
    fieldsets = ((None,{'fields': ('title',)}),)
    list_display = ('title',)
    ordered = ('title',)

class ProducerAdmin(admin.ModelAdmin):
    fieldsets = ((None,{'fields': ('name','country', 'buys')}),)
    list_display = ('name', 'country', 'buys')
    ordered = ('title', 'country')
    search_fields = ('name',)

class CategoryAdmin(admin.ModelAdmin):
    fieldsets = ((None,{'fields': ('title','parent')}),)
    list_display = ('title', 'parent')
    ordered = ('parent', 'title')
    search_fields = ('title',)

class ItemAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Информация',
         {'fields':('title', 'category', 'producer', 'color')}),
        ('Подробности',
         {'fields': ('image', 'desc')}),
        ('Служебное',
         {'fields': ('buys', 'reg_date')})
        )
    list_display = ('title', 'category', 'producer', 'buys')
    ordering = ('title', 'category')
    search_fields = ('title', 'category')

class BuyerAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Основная информация',
         {'fields': ('lastname', 'firstname', 'secondname')}),
        ('Дополнительная информация',
         {'fields': ('address', 'email')})
        )
    list_display = ('lastname', 'firstname')
    ordering = ('lastname', 'firstname')
    search_fields = ('lastname', 'firstname')

class OrderAdmin(admin.ModelAdmin):
    fieldsets = (
        ('О покупателе',
         {'fields': ('buyer', 'comment')}),
        ('Заказ',
         {'fields': ('count', 'totalprice')}),
        ('Доставка',
         {'fields': ('courier', 'status')})
        )
    list_display = ('buyer', 'count', 'totalprice',
                    'reg_date', 'status')
    ordering = ('status', 'totalprice')
    search_fields = ('buyer', 'status')

admin.site.register(Color, ColorAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Producer, ProducerAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Buyer, BuyerAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Order, OrderAdmin)

