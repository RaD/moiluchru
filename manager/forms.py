# -*- coding: utf-8 -*-

from django import forms
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import models as admmodels

from shop import models

class CourierSelect(forms.ModelChoiceField):
    """ Класс предназначен для переопределения метода отображения списка курьеров. """
    def label_from_instance(self, obj):
        return "%s" % obj.get_full_name()
            
class OrderForm(forms.Form):
    status = forms.ModelChoiceField(label=_(u'Status'), queryset=models.OrderStatus.objects.all(),
                                    widget=forms.Select(attrs={'class':'longitem'}))
    courier = CourierSelect(label=_(u'Courier'), required=False,
                            queryset=admmodels.User.objects.filter(groups=1),
                            widget=forms.Select(attrs={'class':'longitem'}))

    def __init__(self, *args, **kwargs):
        for argument in ['order']:
            if argument in kwargs:
                setattr(self, argument, kwargs[argument])
                del kwargs[argument]
        super(OrderForm, self).__init__(*args, **kwargs)

    def save(self):
        c = self.cleaned_data
        status = c['status']
        courier = c.get('courier', None)
        if self.order.status != status or \
                self.order.courier != courier:
            models.OrderStatusChange(order=self.order, courier=courier,
                                     new_status=status,
                                     old_status=self.order.status).save()
            self.order.courier=courier
            self.order.status=status
            self.order.save()

class DiscountForm(forms.Form):
    discount = forms.CharField(label=_(u'Discount, in %'), max_length=2,
                               widget=forms.TextInput(attrs={'class':'right'}))

    def __init__(self, *args, **kwargs):
        for argument in ['order']:
            if argument in kwargs:
                setattr(self, argument, kwargs[argument])
                del kwargs[argument]
        super(DiscountForm, self).__init__(*args, **kwargs)

    def save(self):
        c = self.cleaned_data
        self.order.discount=c['discount']
        self.order.save()
