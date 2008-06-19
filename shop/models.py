# -*- coding: utf-8 -*-

from django.utils.translation import ugettext
from django.utils.translation import gettext_lazy as _
from django.db import models

class Country(models.Model):
    title = models.CharField(ugettext('Title'), max_length=60)

    class Meta:
        verbose_name = _('Country')
        verbose_name_plural = _('Countries')

    class Admin:
        list_display = ('title',)
        ordering = ('title',)

    def __unicode__(self):
        return self.title
    
class City(models.Model):
    title = models.CharField(ugettext('Title'), max_length=60)
    country = models.ForeignKey(Country, verbose_name=ugettext('Country'))

    class Meta:
        verbose_name = _('City')
        verbose_name_plural = _('Cities')

    class Admin:
        list_display = ('title', 'country')
        ordering = ('title', 'country')
        search_fields = ('title',)

    def __unicode__(self):
        return self.title
    
class Producer(models.Model):
    name = models.CharField(ugettext('Company'), max_length=30)
    country = models.ForeignKey(Country, verbose_name=ugettext('Country'))
#    website = models.URLField(verify_exists=False)

    class Meta:
        verbose_name = _('Producer')
        verbose_name_plural = _('Producers')

    class Admin:
        list_display = ('name', 'country')
        ordering = ('name', 'country')
        search_fields = ('name')

    def __unicode__(self):
        return self.name
    
class Category(models.Model):
    """ The categories of items. """
    name = models.CharField(ugettext('Title'), max_length=30)
    parent = models.ForeignKey('self', blank=True, null=True,
                               verbose_name=ugettext('Title'))

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        #order_with_respect_to = 'parent'

    class Admin:
        list_display = ('name', 'parent')
        ordering = ('parent', 'name')
        search_fields = ('name',)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/shop/category/%s" % self.id

    def subcats(self):
        """ Этот метод возвращает список дочерних категорий. """
        return self.categories_set.all()

class Seller(models.Model):
    title = models.CharField(max_length=30)
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=40)
    address = models.CharField(max_length=50)
    city = models.ForeignKey(City)
    email = models.EmailField()
    website = models.URLField(verify_exists=False)
    join_date = models.DateTimeField()
    status = models.BooleanField()
#    headshot = models.ImageField(upload_to='/tmp')

    class Meta:
        verbose_name = _('Seller')
        verbose_name_plural = _('Sellers')

    class Admin:
        list_display = ('title', 'lastname', 'firstname', 'city')
        ordering = ('title', 'lastname', 'firstname')
        search_fields = ('title', 'lastname')

    def __unicode__(self):
        return self.title
    
class Item(models.Model):
    title = models.CharField(max_length=60)
    desc = models.TextField()
    category = models.ForeignKey(Category)
    producer = models.ForeignKey(Producer)
    reg_date = models.DateTimeField()
#    image = models.ImageField(upload_to='/tmp')
    
    class Meta:
        verbose_name = _('Item')
        verbose_name_plural = _('Items')

    class Admin:
        list_display = ('title', 'category', 'producer')
        ordering = ('title', 'category')
        search_fields = ('title', 'category')

    def __unicode__(self):
        return self.title
    
    def get_absolute_url(self):
        return "/shop/item/%s" % self.id
    
class Offer(models.Model):
    item = models.ForeignKey(Item)
    seller = models.ForeignKey(Seller)
    price = models.FloatField()
    color = models.CharField(max_length=60)
    count = models.PositiveIntegerField()
    reg_date = models.DateTimeField()
    
    class Meta:
        verbose_name = _('Offer')
        verbose_name_plural = _('Offers')

    class Admin:
        list_display = ('item', 'seller', 'price', 'color', 'count')
        ordering = ('item', 'seller', 'price', 'color', 'count')
        search_fields = ('item', 'seller')

    def __unicode__(self):
        return self.item.title
    
class Buyer(models.Model):
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=40)
    address = models.CharField(max_length=50)
    email = models.EmailField()
    city = models.ForeignKey(City)
    join_date = models.DateTimeField()
    
    class Meta:
        verbose_name = _('Buyer')
        verbose_name_plural = _('Buyers')

    class Admin:
        list_display = ('lastname', 'firstname', 'city')
        ordering = ('lastname', 'firstname', 'city')
        search_fields = ('lastname', 'firstname')

    def __unicode__(self):
        return self.lastname
    
class OrderStatus(models.Model):
    title = models.CharField(max_length=30)

    class Meta:
        verbose_name = _('Order status')
        verbose_name_plural = _('Order statuses')

    class Admin:
        list_display = ('title',)
	ordering = ('title',)
	search_fields = ('title',)
    
    def __unicode__(self):
        return self.title
    
class Order(models.Model):
    buyer = models.ForeignKey(Buyer)
    count = models.PositiveIntegerField()
    totalprice = models.FloatField()
    reg_date = models.DateTimeField()
    status = models.ForeignKey(OrderStatus)

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    class Admin:
        list_display = ('buyer', 'count', 'totalprice', 'reg_date', 'status')
        ordering = ('status', 'totalprice')
        search_fields = ('buyer', 'status')

    def __unicode__(self):
        return self.buyer
    
class OrderDetail(models.Model):
    order = models.ForeignKey(Order)
    item = models.ForeignKey(Item)
    count = models.PositiveIntegerField()
    price = models.FloatField()

class OrderStatusChange(models.Model):
    order = models.ForeignKey(Order)
    old_status = models.ForeignKey(OrderStatus, related_name="old_status")
    new_status = models.ForeignKey(OrderStatus, related_name="new_status")
    reg_time = models.DateTimeField()

class Courier(models.Model):
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=40)
    parname = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=50)
    city = models.ForeignKey(City)
    seller = models.ForeignKey(Seller)
    join_date = models.DateTimeField()
    status = models.BooleanField()
#    headshot = models.ImageField(upload_to='/tmp')
#    passport = models.ImageField(upload_to='/tmp')

class PhoneType(models.Model):
    title = models.CharField(max_length=20)

class Phone(models.Model):
    number = models.CharField(max_length=20)
    type = models.ForeignKey(PhoneType)
    owner = models.ForeignKey(Buyer)
