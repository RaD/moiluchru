# -*- coding: utf-8 -*-

from django.utils.translation import ugettext, gettext_lazy as _
from django.contrib.admin.models import User
from django.db import models

class Color(models.Model):
    title = models.CharField(ugettext('Title'), max_length=60)

    class Meta:
        verbose_name = _('Color')
        verbose_name_plural = _('Colors')

    def __unicode__(self):
        return self.title
    
class Country(models.Model):
    title = models.CharField(ugettext('Title'), max_length=60)

    class Meta:
        verbose_name = _('Country')
        verbose_name_plural = _('Countries')

    def __unicode__(self):
        return self.title
    
class City(models.Model):
    title = models.CharField(ugettext('Title'), max_length=60)
    country = models.ForeignKey(Country, verbose_name=ugettext('Country'))

    class Meta:
        verbose_name = _('City')
        verbose_name_plural = _('Cities')

    def __unicode__(self):
        return self.title
    
class Producer(models.Model):
    name = models.CharField(ugettext('Company'), max_length=30)
    country = models.ForeignKey(Country, verbose_name=ugettext('Country'))
    buys = models.IntegerField(ugettext('Buys'), default=0)
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
    name = models.CharField(ugettext('Title'), max_length=30)
    parent = models.ForeignKey('self', blank=True, null=True,
                               verbose_name=ugettext('Title'))

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        #order_with_respect_to = 'parent'

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return u'/shop/category/%i/' % self.id

class Item(models.Model):
    title = models.CharField(ugettext('Title'), max_length=60)
    desc = models.TextField()
    category = models.ForeignKey(Category, verbose_name=ugettext('Category'))
    producer = models.ForeignKey(Producer, verbose_name=ugettext('Producer'))
    price = models.FloatField(ugettext('Price'))
    color = models.ForeignKey(Color, verbose_name=ugettext('Color'))
    count = models.PositiveIntegerField(ugettext('Count'))
    reserved = models.PositiveIntegerField(ugettext('Reserved'), default=0)
    reg_date = models.DateTimeField()
    image = models.ImageField(upload_to="itempics", blank=True)
    buys = models.IntegerField(ugettext('Buys'), default=0)
    
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
        return self.lastname
    
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

class Profile(models.Model):
    # обязательная часть профайла
    user = models.ForeignKey(User, unique=True)
    # моё
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=50)
    city = models.ForeignKey(City)
#    headshot = models.ImageField(upload_to='/tmp')
#    passport = models.ImageField(upload_to='/tmp')
    
