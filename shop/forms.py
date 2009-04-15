# -*- coding: utf-8 -*-

from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib.admin import models as admmodels

from moiluchru.shop import models

# Определяем класс для отображения ошибок в пользовательском вводе
class DivErrorList(forms.util.ErrorList):
    def __unicode__(self):
        return self.as_divs()
    def as_divs(self):
        if not self: return u''
        return u'<div class="errorlist">%s</div>' % ''.join([u'<div class="error">%s</div>' % e for e in self])

class CourierSelect(forms.ModelChoiceField):
    """ Класс предназначен для переопределения метода отображения списка курьеров. """
    def label_from_instance(self, obj):
        return "%s" % obj.get_full_name()
            
class SearchForm(forms.Form):
    userinput = forms.CharField(max_length=64)
    howmuch = forms.ChoiceField(choices=[(1, settings.SHOP_ITEMS_PER_PAGE), (2, '10'), (3, '25'), (4, '50')])

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
    phonetype = forms.ModelChoiceField(label=_(u'Phone type'), queryset=models.PhoneType.objects.all(),
                                       widget=forms.Select(attrs={'class':'longitem'}))
    email = forms.EmailField(label=_(u'E-mail'), max_length=75,
                             widget=forms.TextInput(attrs={'class':'longitem'}))
    comment = forms.CharField(label=_(u'Comment'), required=False,
                              widget=forms.Textarea(attrs={'class':'longitem'}))

class LoginForm(forms.Form):
    login = forms.CharField(label=_(u'Login'), max_length=30,
                            widget=forms.TextInput(attrs={'class':'longitem'}))
    passwd = forms.CharField(label=_(u'Password'), max_length=128,
                             widget=forms.PasswordInput(attrs={'class':'longitem'}))

class OrderForm(forms.Form):
    status = forms.ModelChoiceField(label=_(u'Status'), queryset=models.OrderStatus.objects.all(),
                                    widget=forms.Select(attrs={'class':'longitem'}))
    courier = CourierSelect(label=_(u'Courier'), queryset=admmodels.User.objects.filter(groups=1),
                            widget=forms.Select(attrs={'class':'longitem'}))

class CartAdd(forms.Form):
    item = forms.CharField(label=_(u'Item id'), max_length=8)
    count = forms.CharField(label=_(u'Item count'), max_length=8)

class CartClean(forms.Form):
    pass

