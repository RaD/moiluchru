# -*- coding: utf-8 -*-

from django.contrib import admin
from django import forms
from django.utils.translation import gettext_lazy as _

from moiluchru.shop.models import Color, Country, Producer, Category, Collection, \
    Item, ItemType, Price, Buyer, Order

class ColorAdmin(admin.ModelAdmin):
    fieldsets = ((None,{'fields': ('title',)}),)
    list_display = ('title',)
    ordered = ('title',)
admin.site.register(Color, ColorAdmin)

class CountryAdmin(admin.ModelAdmin):
    fieldsets = ((None,{'fields': ('title',)}),)
    list_display = ('title',)
    ordered = ('title',)
admin.site.register(Country, CountryAdmin)

class ProducerAdmin(admin.ModelAdmin):
    fieldsets = ((None,{'fields': ('name','country', 'buys')}),)
    list_display = ('name', 'country', 'buys')
    ordered = ('title', 'country')
    search_fields = ('name',)
admin.site.register(Producer, ProducerAdmin)

class CategoryAdmin(admin.ModelAdmin):
    fieldsets = ((None,{'fields': ('title','parent')}),)
    list_display = ('title', 'parent')
    ordered = ('parent', 'title')
    search_fields = ('title',)
admin.site.register(Category, CategoryAdmin)

class CollectionAdmin(admin.ModelAdmin):
    fieldsets = ((None,{'fields': ('title',)}),)
    list_display = ('title',)
    ordered = ('title',)
    search_fields = ('title',)
admin.site.register(Collection, CollectionAdmin)

### ItemType

class ItemTypeAdmin(admin.ModelAdmin):
    fieldsets = ((None,{'fields': ('title', 'model_name')}),)
    list_display = ('title',)
    ordered = ('title',)
    search_fields = ('title',)
admin.site.register(ItemType, ItemTypeAdmin)

### Item

class ItemForm(forms.ModelForm):
    price_shop = forms.FloatField(label=_(u'Price (shop)'))
    price_store = forms.FloatField(label=_(u'Price (store)'))

    class Meta:
        model = Item

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

def field_price_store(item):
    try:
        # берём самую свежую запись
        return Price.objects.filter(item=item).order_by('-applied')[0].price_store
    except Price.DoesNotExists:
        return '0.00'

field_price_store.short_description = _(u'Price of a store')

def field_price_shop(item):
    try:
        # берём самую свежую запись
        return Price.objects.filter(item=item).order_by('-applied')[0].price_shop
    except Price.DoesNotExists:
        return '0.00'

field_price_shop.short_description = _(u'Price of the shop')

class ItemAdmin(admin.ModelAdmin):
    form = ItemForm
    fieldsets = (
        ('Информация',
         {'fields':(('title', 'color', 'is_present'),
                    ('category', 'producer', 'collection'),
                    ('price_shop', 'price_store'),
                    'item_type')}),
        ('Подробности',
         {'fields': ('image', 'desc')}),
        ('Служебное',
         {'fields': ('buys', 'reg_date')})
        )
    list_display = ('title', 'category', 'producer', 
                    field_price_store, field_price_shop, 'buys')
    ordering = ('title', 'category')
    search_fields = ('title', 'category')

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

admin.site.register(Buyer, BuyerAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Order, OrderAdmin)

