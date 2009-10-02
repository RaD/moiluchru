# -*- coding: utf-8 -*-

import os, re

from django.conf import settings
from django.contrib import admin
from django import forms
from django.utils.translation import ugettext_lazy as _

from snippets import thumbnail

from shop import models

class SocleAdmin(admin.ModelAdmin):
    fieldsets = (('Параметры', {'fields': ('title',)}),)
    list_display = ('title',)

admin.site.register(models.Socle, SocleAdmin)

class ColorAdmin(admin.ModelAdmin):
    fieldsets = ((None,{'fields': ('title','code')}),)
    list_display = ('title','code')
    ordering = ('title',)
admin.site.register(models.Color, ColorAdmin)

class CountryAdmin(admin.ModelAdmin):
    fieldsets = ((None,{'fields': ('title',)}),)
    list_display = ('title',)
    ordering = ('title',)
admin.site.register(models.Country, CountryAdmin)

class ProducerAdmin(admin.ModelAdmin):
    fieldsets = ((None,{'fields': ('name','country', 'buys')}),)
    list_display = ('name', 'country', 'buys')
    ordering = ('name', 'country')
    search_fields = ('name',)
admin.site.register(models.Producer, ProducerAdmin)

### Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = models.Category
        exclude = ('slug', )

class CategoryAdmin(admin.ModelAdmin):
    form = CategoryForm
    fieldsets = ((None,{'fields': ('title', 'parent')}),)
    list_display = ('title', 'slug', 'parent')
    ordering = ('parent', 'title')
    search_fields = ('title',)
admin.site.register(models.Category, CategoryAdmin)

class CollectionAdmin(admin.ModelAdmin):
    fieldsets = ((None,{'fields': ('title',)}),)
    list_display = ('title',)
    ordering = ('title',)
    search_fields = ('title',)
admin.site.register(models.Collection, CollectionAdmin)

class ItemTypeAdmin(admin.ModelAdmin):
    fieldsets = ((None,{'fields': ('title', 'model_name')}),)
    list_display = ('title', 'model_name')
    ordering = ('title', 'model_name')
    search_fields = ('title', 'model_name')
admin.site.register(models.ItemType, ItemTypeAdmin)

### Item

class ItemForm(forms.ModelForm):
    price_shop = forms.FloatField(label=_(u'Price (shop)'))
    price_store = forms.FloatField(label=_(u'Price (store)'))

    class Meta:
        model = models.Item

    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        if self.instance:
            (self.fields['price_store'].initial,
             self.fields['price_shop'].initial) = self.instance.get_price()

    def save(self, *args, **kwargs):
        d = self.cleaned_data
        m = super(ItemForm, self).save(*args, **kwargs)
        price_store = d.get('price_store')
        price_shop = d.get('price_shop')
        if m and d.get('price_store') and d.get('price_shop'):
            m.set_price(price_store, price_shop)
        return m

class LampInline(admin.TabularInline):
    model = models.Lamp
    extra = 1
      
class EslLampInline(admin.TabularInline):
    model = models.EslLamp
    max_num = 1
      
class SizeInline(admin.TabularInline):
    model = models.Size
    max_num = 1
      
class IntegratedInline(admin.TabularInline):
    model = models.IntegratedLight
    max_num = 1
      
class ItemAdmin(admin.ModelAdmin):
    form = ItemForm
    fieldsets = (
        ('Информация',
         {'fields':(('title', 'color'), ('is_present', 'has_lamp'),
                    ('category', 'producer', 'collection'),
                    ('price_shop', 'price_store'),
                    'item_type')}),
        ('Подробности',
         {'fields': ('image', 'desc', 'tags')})
        )
    list_display = ('title', 'field_image_preview', 'category',
                    'field_price_shop', 'buys', 'reg_date')
    ordering = ('-reg_date', 'title', 'category')
    search_fields = ('title', 'category')
    save_as = True
    inlines = [eval('%sInline' % model_name) for model_name in settings.SHOP_INLINES]

    def field_image_preview(self, item):
        url = thumbnail(item.image.path, '100x,itempics')
        return '<img src="%s"/>' % url
    field_image_preview.short_description = _(u'Preview')
    field_image_preview.allow_tags = True
    
    def field_price_store(self, item):
        try:
            # берём самую свежую запись
            return models.Price.objects.filter(item=item).order_by('-applied')[0].price_store
        except models.Price.DoesNotExists:
            return '0.00'
    field_price_store.short_description = _(u'Price of a store')

    def field_price_shop(self, item):
        try:
            # берём самую свежую запись
            return models.Price.objects.filter(item=item).order_by('-applied')[0].price_shop
        except models.Price.DoesNotExists:
            return '0.00'
    field_price_shop.short_description = _(u'Price of the shop')

admin.site.register(models.Item, ItemAdmin)

###

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

admin.site.register(models.Buyer, BuyerAdmin)

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

admin.site.register(models.Order, OrderAdmin)

