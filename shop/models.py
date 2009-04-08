# -*- coding: utf-8 -*-

from django.utils.translation import gettext_lazy as _
from django.contrib.admin.models import User
from django.db import models

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
    title = models.CharField(_('Title'), max_length=64)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.title

# Наследуем класс от entity
class Color(CommonEntity):
    pass

    class Meta:
        verbose_name = _('Color')
        verbose_name_plural = _('Colors')

# Наследуем класс от entity
class Country(CommonEntity):
    pass

    class Meta:
        verbose_name = _('Country')
        verbose_name_plural = _('Countries')

class Producer(models.Model):
    name = models.CharField(_('Company'), max_length=30)
    country = models.ForeignKey(Country, verbose_name=_('Country'))
    buys = models.PositiveIntegerField(_('Buys'), default=0)
#    website = models.URLField(verify_exists=False)

    class Meta:
        verbose_name = _('Producer')
        verbose_name_plural = _('Producers')

    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        return u'/shop/producer/%i/' % self.id

# Наследуем класс от entity
class Category(CommonEntity):
    """ The categories of items. """
    parent = models.ForeignKey('self', blank=True, null=True,
                               verbose_name=_('Parent'))

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def get_absolute_url(self):
        return u'/shop/category/%i/' % self.id

# Наследуем класс от entity
class Collection(CommonEntity):
    """ The collection for items. """
    pass

    class Meta:
        verbose_name = _('Collection')
        verbose_name_plural = _('Collections')

    def get_absolute_url(self):
        return u'/shop/collection/%i/' % self.id

# Наследуем класс от entity
class ItemType(CommonEntity):
    """ The collection for items. """
    model_name = models.CharField(_(u'Name of model'), max_length=64)

    class Meta:
        verbose_name = _('Model name')
        verbose_name_plural = _('Model name')

class Item(CommonEntity):
    desc = models.TextField()
    item_type = models.ForeignKey(ItemType, verbose_name=_('Item type'))
    category = models.ForeignKey(Category, verbose_name=_('Category'))
    collection = models.ForeignKey(Collection, verbose_name=_('Collection'), null=True)
    producer = models.ForeignKey(Producer, verbose_name=_('Producer'))
    color = models.ForeignKey(Color, verbose_name=_('Color'))
    is_present = models.BooleanField(_('Is present'))
    reg_date = models.DateTimeField()
    image = models.ImageField(upload_to="itempics")
    buys = models.IntegerField(_('Buys'), default=0)
    
    class Meta:
        verbose_name = _('Item')
        verbose_name_plural = _('Items')

    def get_absolute_url(self):
        return u'/shop/item/%i/' % self.id

class Price(models.Model):
    item = models.ForeignKey(Item)
    price_shop = models.FloatField(_('Price (shop)'))
    price_store = models.FloatField(_('Price (store)'))
    applied = models.DateTimeField()
    
    class Meta:
        verbose_name = _('Price')
        verbose_name_plural = _('Prices')

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
        verbose_name = _('Buyer')
        verbose_name_plural = _('Buyers')

    def __unicode__(self):
        return u'%s %s %s' %(self.lastname,
                             self.firstname, self.secondname)
    
class OrderStatus(CommonEntity):
    pass

    class Meta:
        verbose_name = _('Order status')
        verbose_name_plural = _('Order statuses')

class Order(models.Model):
    buyer = models.ForeignKey(Buyer)
    count = models.PositiveIntegerField(default=0)
    totalprice = models.FloatField()
    comment = models.TextField(blank=True, default='')
    reg_date = models.DateTimeField(auto_now_add=True)
    status = models.ForeignKey(OrderStatus)
    courier = models.ForeignKey(User, null=True)

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    def __unicode__(self):
        return self.buyer.lastname
    
    def get_absolute_url(self):
        """ This returns the absolute URL for a record. """
        return u'/shop/orderinfo/%i/' % self.id
    
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
    old_status = models.ForeignKey(OrderStatus, related_name="old_status")
    new_status = models.ForeignKey(OrderStatus, related_name="new_status")
    reg_time = models.DateTimeField(auto_now_add=True)

class PhoneType(CommonEntity):
    pass

    class Meta:
        verbose_name = _('Phone type')
        verbose_name_plural = _('Phone types')
    
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
        verbose_name = _('Socle')
        verbose_name_plural = _('Socles')

class Lamp(models.Model):
    socle = models.ForeignKey(Socle)
    watt = models.PositiveIntegerField(_(u'Power'), default=0)
    count = models.PositiveIntegerField(_(u'Count of lamps'), default=1)
    voltage = models.PositiveIntegerField(_(u'Voltage'), default=0)

