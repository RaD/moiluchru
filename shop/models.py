# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.admin.models import User
from django.utils.translation import ugettext_lazy as _

from datetime import datetime
from tagging.fields import TagField
from tagging.utils import parse_tag_input

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
    code = models.CharField(verbose_name=_(u'Code of color'), max_length=6, default="ffffff")

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

# class AutoManager(models.Manager):
#     def get_query_set(self):
#         qs = super(AutoManager, self).get_query_set()
#         print qs
#         return qs

# Наследуем класс от entity
class Category(CommonEntity):
    """ The categories of items. """
    parent = models.ForeignKey(u'self', blank=True, null=True,
                               verbose_name=_(u'Parent'))
    slug = models.CharField(_(u'Slug'), max_length=255)

    #objects = AutoManager()

    class Meta:
        verbose_name = _(u'Category')
        verbose_name_plural = _(u'Categories')

    def get_absolute_url(self):
        return u'/category/%s/' % self.slug

# Наследуем класс от entity
class Collection(CommonEntity):
    """ The collection for items. """
    pass

    class Meta:
        verbose_name = _(u'Collection')
        verbose_name_plural = _(u'Collections')

    def get_absolute_url(self):
        return u'/collection/%i/' % self.id

class ItemType(CommonEntity):
    """ The collection for items. """
    model_name = models.CharField(_(u'Name of model'), max_length=64)

    class Meta:
        verbose_name = _(u'Item type')
        verbose_name_plural = _(u'Item types')

class Item(CommonEntity):
    desc = models.TextField(verbose_name=_(u'Description'), null=True, blank=True)
    item_type = models.ForeignKey(ItemType, verbose_name=_(u'Item type'))
    category = models.ForeignKey(Category, verbose_name=_(u'Category'))
    collection = models.ForeignKey(Collection, verbose_name=_(u'Collection'), null=True, blank=True)
    producer = models.ForeignKey(Producer, verbose_name=_(u'Producer'))
    color = models.ForeignKey(Color, verbose_name=_(u'Color'))
    is_present = models.BooleanField(verbose_name=_(u'Is present'), 
                                     help_text=_(u'An item is present at store'))
    has_lamp = models.BooleanField(verbose_name=_(u'Has lamp'))
    reg_date = models.DateTimeField(verbose_name=_(u'Defined'), auto_now_add=True)
    last_modification = models.DateTimeField(verbose_name=_(u'Last modification'), auto_now_add=True, auto_now=True)
    image = models.ImageField(verbose_name=_(u'Image'), upload_to=u'itempics')
    buys = models.IntegerField(verbose_name=_(u'Buys'), default=0)
    sort_price = models.FloatField(_(u'Price'), help_text=_(u'Price of an item, in roubles'))
    tags = TagField()
    
    class Meta:
        verbose_name = _(u'Item')
        verbose_name_plural = _(u'Items')

    def get_absolute_url(self):
        return u'/item/%i/' % self.id

    def get_absolute_url_by_title(self):
        return u'/item/%s/' % self.title

    def get_addons(self):
        related = [Size, Lamp, EslLamp]
        objects = {}
        for model in related:
            try:
                objects.update({model.__name__: model.objects.filter(item=self)})
            except model.DoesNotExist:
                pass
        return objects

    def get_price(self):
        try:
            obj = Price.objects.filter(item=self).order_by('-applied')[0]
            price_store = obj.price_store
            price_shop = obj.price_shop
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

    def get_tag_list(self):
        return parse_tag_input(self.tags)

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
    discount = models.PositiveIntegerField(default=0)
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
    courier = models.ForeignKey(User, null=True)
    old_status = models.ForeignKey(OrderStatus, related_name=u'old_status')
    new_status = models.ForeignKey(OrderStatus, related_name=u'new_status')
    reg_date = models.DateTimeField(auto_now_add=True)

class Phone(models.Model):
    number = models.CharField(max_length=20)
    owner = models.ForeignKey(Buyer)


##
## Статистика поисковых запросов
##

class SearchStatQuery(models.Model):
    ip_address = models.IPAddressField()

    class Meta:
        verbose_name = _(u'Search statistic query')
        verbose_name_plural = _(u'Search statistic query')

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            request = kwargs['request']
            self.post = request.POST
            self.meta = request.META
            del kwargs['request']
        super(SearchStatQuery, self).__init__(*args, **kwargs)
        self.ip_address = self.meta.get('REMOTE_ADDR', '127.0.0.127')

    def save(self, *args, **kwargs):
        super(SearchStatQuery, self).save()
        for param in self.post.keys():
            value = self.post[param]
            if param in ['go', 'howmuch', 'simple']:
                continue
            if param.endswith('_0') and value == '0':
                base_param_name = param[0:param.rfind('_')]
                pair_param = '%s_1' % (base_param_name, )
                pair_value = self.post[pair_param]
                if pair_value == '0':
                    continue
            if param.endswith('_1') and value == '0':
                base_param_name = param[0:param.rfind('_')]
                pair_param = '%s_0' % (base_param_name, )
                pair_value = self.post[pair_param]
                if pair_value == '0':
                    continue
            if value == '':
                continue
            SearchStatOption(query=self, param=param, value=value).save()

class SearchStatOption(models.Model):
    query = models.ForeignKey(SearchStatQuery)
    param = models.CharField(max_length=64)
    value = models.CharField(max_length=1024)

    class Meta:
        verbose_name = _(u'Search statistic option')
        verbose_name_plural = _(u'Search statistic options')

##
## Определение специфических свойств товара
##

class Size(models.Model):
    item = models.ForeignKey(Item)
    diameter = models.PositiveIntegerField(verbose_name=_(u'Diameter'), 
                                           help_text=_(u'Diameter of an item, in millimeters'),
                                           null=True, blank=True)
    height = models.PositiveIntegerField(verbose_name=_(u'Height'), 
                                         help_text=_(u'Height of an item, in millimeters'),
                                         null=True, blank=True)
    length = models.PositiveIntegerField(verbose_name=_(u'Length'), 
                                         help_text=_(u'Length of an item, in millimeters'),
                                         null=True, blank=True)
    width = models.PositiveIntegerField(verbose_name=_(u'Width'), 
                                        help_text=_(u'Width of an item, in millimeters'),
                                        null=True, blank=True)
    brow = models.PositiveIntegerField(verbose_name=_(u'Brow'), 
                                       help_text=_(u'Brow of an item, in millimeters'),
                                       null=True, blank=True)
# Освещение
class Socle(CommonEntity):
    pass

    class Meta:
        verbose_name = _(u'Socle')
        verbose_name_plural = _(u'Socles')

class Lamp(models.Model):
    item = models.ForeignKey(Item)
    socle = models.ForeignKey(Socle, 
                              verbose_name=_(u'Socle'),
                              help_text=_(u'Socle of lamp'))
    watt = models.PositiveIntegerField(verbose_name=_(u'Power'), default=0,
                                       help_text=_(u'Power of lamp'))
    count = models.PositiveIntegerField(verbose_name=_(u'Count of lamps'), 
                                        help_text=_(u'Count of lamps'), default=1)
    voltage = models.PositiveIntegerField(verbose_name=_(u'Voltage'),
                                          help_text=_(u'Voltage of lamps'), default=220)

class IntegratedLight(models.Model):
    item = models.ForeignKey(Item)
    color = models.ForeignKey(Color, verbose_name=_(u'Color'))
    montage_diameter = models.PositiveIntegerField(
        verbose_name=_(u'Diameter of an hole'), 
        help_text=_(u'Diameter of an montage hole, in millimeters'),
        null=True, blank=True)
    
# Энергосберегающие лампы
class EslLamp(models.Model):
    item = models.ForeignKey(Item)
    socle = models.ForeignKey(Socle, 
                              verbose_name=_(u'Socle'),
                              help_text=_(u'Socle of lamp'))
    consumption = models.PositiveIntegerField(verbose_name=_(u'Consuption'), default=0,
                                              help_text=_(u'Consumption of lamp in Watts'))
    luminosity = models.PositiveIntegerField(verbose_name=_(u'Luminosity'), default=0,
                                              help_text=_(u'Luminosity of lamp in Watts'))
    temperature = models.PositiveIntegerField(verbose_name=_(u'Temperature'), default=0,
                                              help_text=_(u'Light\'s temperature in K'))
    voltage = models.PositiveIntegerField(verbose_name=_(u'Voltage'), 
                                          help_text=_(u'Voltage of lamps'), default=220)
