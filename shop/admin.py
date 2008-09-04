# -*- coding: utf-8 -*-

from django.contrib import admin
from cargo.shop.models import Color, Country, City, Producer, Category, Item, Buyer, Order, Howto

class ColorAdmin(admin.ModelAdmin):
    fieldsets = ((None,{'fields': ('title',)}),)
    list_display = ('title',)
    ordered = ('title',)

class CountryAdmin(admin.ModelAdmin):
    fieldsets = ((None,{'fields': ('title',)}),)
    list_display = ('title',)
    ordered = ('title',)

class CityAdmin(admin.ModelAdmin):
    fieldsets = ((None,{'fields': ('title','country')}),)
    list_display = ('title', 'country')
    ordered = ('title', 'country')
    search_fields = ('title',)

class ProducerAdmin(admin.ModelAdmin):
    fieldsets = ((None,{'fields': ('name','country', 'buys')}),)
    list_display = ('name', 'country', 'buys')
    ordered = ('title', 'country')
    search_fields = ('name',)

class CategoryAdmin(admin.ModelAdmin):
    fieldsets = ((None,{'fields': ('name','parent')}),)
    list_display = ('name', 'parent')
    ordered = ('parent', 'title')
    search_fields = ('name',)

class ItemAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Информация',
         {'fields':('title', 'category', 'producer',
                    'price', 'color', 'count')}),
        ('Подробности',
         {'fields': ('image', 'desc')}),
        ('Служебное',
         {'fields': ('reserved', 'buys', 'reg_date')})
        )
    list_display = ('title', 'category', 'producer',
                    'price', 'count', 'buys')
    ordering = ('title', 'category')
    search_fields = ('title', 'category')

class BuyerAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Основная информация',
         {'fields': ('lastname', 'firstname', 'secondname')}),
        ('Дополнительная информация',
         {'fields': ('address', 'city', 'email')})
        )
    list_display = ('lastname', 'firstname', 'city')
    ordering = ('lastname', 'firstname', 'city')
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

class HowtoAdmin(admin.ModelAdmin):
    fieldsets = ((None,{'fields':
                        ('key', 'title', 'text')}),)
    list_display = ('key', 'title')
    ordering = ('key',)

admin.site.register(Color, ColorAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Producer, ProducerAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Buyer, BuyerAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Howto, HowtoAdmin)

