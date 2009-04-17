# -*- coding: utf-8 -*-

from datetime import datetime

from django.db import models
from django.contrib.admin.models import User
from django.utils.translation import gettext_lazy as _

class Profile(models.Model):
    # обязательная часть профайла
    user = models.ForeignKey(User, unique=True)
    # моё
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=50)
#    headshot = models.ImageField(upload_to='/tmp')
#    passport = models.ImageField(upload_to='/tmp')
    
# Определяем абстрактный класс для Entity
class CommonEntity(models.Model):
    title = models.CharField(verbose_name=_(u'Title'), max_length=64)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.title

# Наследуем класс от entity
class Color(CommonEntity):
    pass

    class Meta:
        verbose_name = _(u'Color')
        verbose_name_plural = _(u'Colors')

# Наследуем класс от entity
class Country(CommonEntity):
    pass

    class Meta:
        verbose_name = _(u'Country')
        verbose_name_plural = _(u'Countries')

class Producer(models.Model):
    name = models.CharField(_(u'Company'), max_length=30)
    country = models.ForeignKey(Country, verbose_name=_(u'Country'))
    buys = models.PositiveIntegerField(_(u'Buys'), default=0)
#    website = models.URLField(verify_exists=False)

    class Meta:
        verbose_name = _(u'Producer')
        verbose_name_plural = _(u'Producers')

    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        return u'/shop/producer/%i/' % self.id

# Наследуем класс от entity
class Category(CommonEntity):
    """ The categories of items. """
    parent = models.ForeignKey(u'self', blank=True, null=True,
                               verbose_name=_(u'Parent'))

    class Meta:
        verbose_name = _(u'Category')
        verbose_name_plural = _(u'Categories')

    def get_absolute_url(self):
        return u'/shop/category/%i/' % self.id

# Наследуем класс от entity
class Collection(CommonEntity):
    """ The collection for items. """
    pass

    class Meta:
        verbose_name = _(u'Collection')
        verbose_name_plural = _(u'Collections')

    def get_absolute_url(self):
        return u'/shop/collection/%i/' % self.id

class ItemType(CommonEntity):
    """ The collection for items. """
    model_name = models.CharField(_(u'Name of model'), max_length=64)

    #class Meta:
    #    verbose_name = _(u'Item type')
    #    verbose_name_plural = _(u'Item types')

class Item(CommonEntity):
    desc = models.TextField(verbose_name=_(u'Description'), null=True, blank=True)
    item_type = models.ForeignKey(ItemType, verbose_name=_(u'Item type'))
    category = models.ForeignKey(Category, verbose_name=_(u'Category'))
    collection = models.ForeignKey(Collection, verbose_name=_(u'Collection'), null=True, blank=True)
    producer = models.ForeignKey(Producer, verbose_name=_(u'Producer'))
    color = models.ForeignKey(Color, verbose_name=_(u'Color'))
    is_present = models.BooleanField(verbose_name=_(u'Is present'))
    has_lamp = models.BooleanField(verbose_name=_(u'Has lamp'))
    reg_date = models.DateTimeField(verbose_name=_(u'Defined'), auto_now_add=True)
    image = models.ImageField(verbose_name=_(u'Image'), upload_to=u'itempics')
    buys = models.IntegerField(verbose_name=_(u'Buys'), default=0)
    sort_price = models.FloatField(_(u'Price'))
    
    class Meta:
        verbose_name = _(u'Item')
        verbose_name_plural = _(u'Items')

    def get_absolute_url(self):
        return u'/shop/item/%i/' % self.id

    def get_lamp(self):
        try:
            return Lamp.objects.filter(item=self)
        except Lamp.DoesNotExist:
            return None

    def get_size(self):
        try:
            return Size.objects.get(item=self)
        except Size.DoesNotExist:
            return None

    def get_price(self):
        try:
            price_store = Price.objects.filter(item=self).order_by('-applied')[0].price_store
            price_shop = Price.objects.filter(item=self).order_by('-applied')[0].price_shop
            return (price_store, price_shop)
        except:
            return (float(0.00), float(0.00))

    def set_price(self, store, shop):
        # надо обязательно сохранить сам объект, только после этого
        # можно сохранять зависимые объекты
        self.sort_price = shop # эта цена используется при сортировке
        self.save()
        # сохраняем информацию о цене
        price = Price(item=self, price_store=store, price_shop=shop, 
                      applied=datetime.now())
        price.save()
            
class Price(models.Model):
    item = models.ForeignKey(Item)
    price_store = models.FloatField(_(u'Price (store)'))
    price_shop = models.FloatField(_(u'Price (shop)'))
    applied = models.DateTimeField()
    
    class Meta:
        verbose_name = _(u'Price')
        verbose_name_plural = _(u'Prices')

    def __unicode__(self):
        return '%s : %s' % (self.price_shop, self.price_store)
    
class Buyer(models.Model):
    lastname = models.CharField(max_length=64)
    firstname = models.CharField(max_length=64)
    secondname = models.CharField(max_length=64)
    address = models.CharField(max_length=255)
    email = models.EmailField()
    join_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _(u'Buyer')
        verbose_name_plural = _(u'Buyers')

    def __unicode__(self):
        return u'%s %s %s' %(self.lastname,
                             self.firstname, self.secondname)
    
class OrderStatus(CommonEntity):
    pass

    class Meta:
        verbose_name = _(u'Order status')
        verbose_name_plural = _(u'Order statuses')

class Order(models.Model):
    buyer = models.ForeignKey(Buyer)
    count = models.PositiveIntegerField(default=0)
    totalprice = models.FloatField()
    comment = models.TextField(blank=True, default=u'')
    reg_date = models.DateTimeField(auto_now_add=True)
    status = models.ForeignKey(OrderStatus)
    courier = models.ForeignKey(User, null=True)

    class Meta:
        verbose_name = _(u'Order')
        verbose_name_plural = _(u'Orders')

    def __unicode__(self):
        return self.buyer.lastname
    
    def get_absolute_url(self):
        """ This returns the absolute URL for a record. """
        return u'/manager/orderinfo/%i/' % self.id
    
class OrderDetail(models.Model):
    order = models.ForeignKey(Order)
    item = models.ForeignKey(Item)
    count = models.PositiveIntegerField(default=0)
    price = models.FloatField()

    def __unicode__(self):
        return self.item.title

class OrderStatusChange(models.Model):
    order = models.ForeignKey(Order)
    courier = models.ForeignKey(User)
    old_status = models.ForeignKey(OrderStatus, related_name=u'old_status')
    new_status = models.ForeignKey(OrderStatus, related_name=u'new_status')
    reg_date = models.DateTimeField(auto_now_add=True)

class PhoneType(CommonEntity):
    pass

    class Meta:
        verbose_name = _(u'Phone type')
        verbose_name_plural = _(u'Phone types')
    
class Phone(models.Model):
    number = models.CharField(max_length=20)
    type = models.ForeignKey(PhoneType)
    owner = models.ForeignKey(Buyer)

##
## Определение специфических свойств товара
##

# Освещение
class Socle(CommonEntity):
    pass

    class Meta:
        verbose_name = _(u'Socle')
        verbose_name_plural = _(u'Socles')

class Lamp(models.Model):
    item = models.ForeignKey(Item)
    socle = models.ForeignKey(Socle)
    watt = models.PositiveIntegerField(_(u'Power'), default=0)
    count = models.PositiveIntegerField(_(u'Count of lamps'), default=1)
    voltage = models.PositiveIntegerField(_(u'Voltage'), default=220)

class Size(models.Model):
    item = models.ForeignKey(Item)
    diameter = models.PositiveIntegerField(_(u'Diameter'), null=True, blank=True)
    height = models.PositiveIntegerField(_(u'Height'), null=True, blank=True)
    length = models.PositiveIntegerField(_(u'Length'), null=True, blank=True)
    width = models.PositiveIntegerField(_(u'Width'), null=True, blank=True)
    brow = models.PositiveIntegerField(_(u'Brow'), null=True, blank=True)
