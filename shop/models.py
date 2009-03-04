# -*- coding: utf-8 -*-

from django.utils.translation import gettext_lazy as _
from django.contrib.admin.models import User
from django.db import models

# Определяем абстрактный класс для Entity
class CommonEntity(models.Model):
    title = models.CharField(_('Title'), max_length=60)

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

# Наследуем класс от entity
class City(CommonEntity):
    country = models.ForeignKey(Country, verbose_name=_('Country'))

    class Meta:
        verbose_name = _('City')
        verbose_name_plural = _('Cities')
    
class Producer(models.Model):
    name = models.CharField(_('Company'), max_length=30)
    country = models.ForeignKey(Country, verbose_name=_('Country'))
    buys = models.IntegerField(_('Buys'), default=0)
#    website = models.URLField(verify_exists=False)

    class Meta:
        verbose_name = _('Producer')
        verbose_name_plural = _('Producers')

    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        return u'/shop/producer/%i/' % self.id

class Category(models.Model):
    """ The categories of items. """
    name = models.CharField(_('Title'), max_length=30)
    parent = models.ForeignKey('self', blank=True, null=True,
                               verbose_name=_('Parent'))

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        #order_with_respect_to = 'parent'

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return u'/shop/category/%i/' % self.id

class Item(models.Model):
    title = models.CharField(_('Title'), max_length=60)
    desc = models.TextField()
    category = models.ForeignKey(Category, verbose_name=_('Category'))
    producer = models.ForeignKey(Producer, verbose_name=_('Producer'))
    price = models.FloatField(_('Price'))
    color = models.ForeignKey(Color, verbose_name=_('Color'))
    count = models.PositiveIntegerField(_('Count'))
    reserved = models.PositiveIntegerField(_('Reserved'), default=0)
    reg_date = models.DateTimeField()
    image = models.ImageField(upload_to="itempics")
    buys = models.IntegerField(_('Buys'), default=0)
    
    class Meta:
        verbose_name = _('Item')
        verbose_name_plural = _('Items')

    def __unicode__(self):
        return self.title
    
    def get_absolute_url(self):
        return u'/shop/item/%i/' % self.id
    
class Buyer(models.Model):
    lastname = models.CharField(max_length=64)
    firstname = models.CharField(max_length=64)
    secondname = models.CharField(max_length=64)
    address = models.CharField(max_length=255)
    email = models.EmailField()
    city = models.ForeignKey(City)
    join_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Buyer')
        verbose_name_plural = _('Buyers')

    def __unicode__(self):
        return u'%s %s %s' %(self.lastname,
                             self.firstname, self.secondname)
    
class OrderStatus(models.Model):
    title = models.CharField(max_length=30)

    class Meta:
        verbose_name = _('Order status')
        verbose_name_plural = _('Order statuses')

    def __unicode__(self):
        return self.title
    
class Order(models.Model):
    buyer = models.ForeignKey(Buyer)
    count = models.PositiveIntegerField()
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
    count = models.PositiveIntegerField()
    price = models.FloatField()

    def __unicode__(self):
        return self.item.title

class OrderStatusChange(models.Model):
    order = models.ForeignKey(Order)
    old_status = models.ForeignKey(OrderStatus, related_name="old_status")
    new_status = models.ForeignKey(OrderStatus, related_name="new_status")
    courier = models.ForeignKey(User)
    reg_time = models.DateTimeField(auto_now_add=True)

class PhoneType(models.Model):
    title = models.CharField(max_length=20)

    class Meta:
        verbose_name = _('Phone type')
        verbose_name_plural = _('Phone types')

    def __unicode__(self):
        return self.title
    
class Phone(models.Model):
    number = models.CharField(max_length=20)
    type = models.ForeignKey(PhoneType)
    owner = models.ForeignKey(Buyer)

class Howto(models.Model):
    key = models.CharField(max_length=32)
    title = models.CharField(max_length=32)
    text = models.TextField()

    class Meta:
        verbose_name = _('Text')
        verbose_name_plural = _('Texts')

    class Admin:
        list_display = ('key', 'title')
        ordering = ('key',)

    def __unicode__(self):
        return self.key

    def get_absolute_url(self):
        """ This returns the absolute URL for a record. """
        return u'/shop/howto/%i/' % self.id


class Support(models.Model):
    title = models.CharField(max_length=64)
    text = models.TextField()

class Profile(models.Model):
    # обязательная часть профайла
    user = models.ForeignKey(User, unique=True)
    # моё
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=50)
    city = models.ForeignKey(City)
#    headshot = models.ImageField(upload_to='/tmp')
#    passport = models.ImageField(upload_to='/tmp')
    
