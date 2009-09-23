# -*- coding: utf-8 -*-

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from shop import models

class OfferForm(forms.Form):
    fname = forms.CharField(label=_(u'Last name'), max_length=64,
                            widget=forms.TextInput(attrs={'class':'longitem'}))
    iname = forms.CharField(label=_(u'First name'), max_length=64,
                            widget=forms.TextInput(attrs={'class':'longitem'}))
    oname = forms.CharField(label=_(u'Second name'), max_length=64,
                            widget=forms.TextInput(attrs={'class':'longitem'}))
    address = forms.CharField(label=_(u'Address'), max_length=255,
                              widget=forms.TextInput(attrs={'class':'longitem'}))
    phone = forms.CharField(label=_(u'Contact phone'), max_length=20,
                            widget=forms.TextInput(attrs={'class':'longitem'}))
    email = forms.EmailField(label=_(u'E-mail'), max_length=75,
                             widget=forms.TextInput(attrs={'class':'longitem'}))
    comment = forms.CharField(label=_(u'Comment'), required=False,
                              widget=forms.Textarea(attrs={'class':'longitem'}))

    def __init__(self, *args, **kwargs):
        for argument in ['cart', 'count', 'total']:
            if argument in kwargs:
                setattr(self, argument, kwargs[argument])
                del kwargs[argument]
        super(OfferForm, self).__init__(*args, **kwargs)

    def save(self):
        clean = self.cleaned_data
        buyer, created = models.Buyer.objects.get_or_create(
            lastname = clean['fname'], 
            firstname = clean['iname'], 
            secondname = clean['oname'],
            address = clean['address'], 
            email =  clean['email']
            )
        phone, created = models.Phone.objects.get_or_create(
            number = clean['phone'], 
            owner = buyer
            )
        order, created = models.Order.objects.get_or_create(
            buyer = buyer,
            count = self.count,
            totalprice = self.total,
            comment = clean['comment'],
            status = models.OrderStatus.objects.get(id=1)
            )
        for i in self.cart.keys():
            item = models.Item.objects.get(id=i)
            orderdetail = models.OrderDetail(order = order, item = item,
                                             count = self.cart[i]['count'],
                                             price = self.cart[i]['price'])
            orderdetail.save()
        # убираем товар с витрины
        item.buys += 1
        item.save()

class LoginForm(forms.Form):
    login = forms.CharField(label=_(u'Login'), max_length=30,
                            widget=forms.TextInput(attrs={'class':'longitem'}))
    passwd = forms.CharField(label=_(u'Password'), max_length=128,
                             widget=forms.PasswordInput(attrs={'class':'longitem'}))

class CartAdd(forms.Form):
    item = forms.CharField(label=_(u'Item id'), max_length=8)
    count = forms.CharField(label=_(u'Item count'), max_length=8)

class CartClean(forms.Form):
    pass

class CartRecalculate(forms.Form):
    item = forms.CharField(label=_(u'Item id'), max_length=8)
    count = forms.CharField(label=_(u'Item count'), max_length=8)

class CartRemoveItem(forms.Form):
    item = forms.CharField(label=_(u'Item id'), max_length=8)
