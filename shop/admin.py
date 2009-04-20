# -*- coding: utf-8 -*-

from django.contrib import admin
from django import forms
from django.utils.translation import gettext_lazy as _

from moiluchru.shop.models import Color, Country, Producer, Category, \
     Collection, Item, ItemType, Price, Buyer, Order
from moiluchru.shop.models import Lamp, Size, Socle

class SocleAdmin(admin.ModelAdmin):
    fieldsets = (('Параметры', {'fields': ('title',)}),)
    list_display = ('title',)

admin.site.register(Socle, SocleAdmin)

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

class LampInline(admin.TabularInline):
    model = Lamp
    extra = 1
      
class SizeInline(admin.TabularInline):
    model = Size
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
    list_display = ('title', 'category', 'field_price_shop', 
                    'buys', 'reg_date')
    ordering = ('title', 'category')
    search_fields = ('title', 'category')
    save_as = True
    inlines = [SizeInline, LampInline]

    def __init__(self, *args, **kwargs):
        super(ItemAdmin, self).__init__(*args, **kwargs)
        """ Дмитрий Аникин: может быть стоит сделать у class ItemAdmin
        функцию __init__() и в ней прописать это условие, которое будет
        списку inlines присваивать нужный класс-наследний
        admin.TabularInline?"""
        try:
            pass
            #item_type = Item.objects.get(id=args[0].id)
#             print item_type
            #print args[0].item_type
            #print args[0].item_type.field
            #self.inline = eval('[%sInline]' % model_name)
        except Exception, e:
            print e
            self.inline = []
        
    def field_price_store(self, item):
        try:
            # берём самую свежую запись
            return Price.objects.filter(item=item).order_by('-applied')[0].price_store
        except Price.DoesNotExists:
            return '0.00'
    field_price_store.short_description = _(u'Price of a store')

    def field_price_shop(self, item):
        try:
            # берём самую свежую запись
            return Price.objects.filter(item=item).order_by('-applied')[0].price_shop
        except Price.DoesNotExists:
            return '0.00'
    field_price_shop.short_description = _(u'Price of the shop')

admin.site.register(Item, ItemAdmin)
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

admin.site.register(Buyer, BuyerAdmin)

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

admin.site.register(Order, OrderAdmin)

