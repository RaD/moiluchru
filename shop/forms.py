# -*- coding: utf-8 -*-

from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib.admin import models as admmodels

from shop import models

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

class CartRecalculate(forms.Form):
    item = forms.CharField(label=_(u'Item id'), max_length=8)
    count = forms.CharField(label=_(u'Item count'), max_length=8)

class CartRemoveItem(forms.Form):
    item = forms.CharField(label=_(u'Item id'), max_length=8)

##
## ПОИСКОВЫЙ ИНТЕРФЕЙС
##

from django.forms.models import ModelFormMetaclass
from django.forms.fields import IntegerField
from django.utils.datastructures import SortedDict

class MinMaxWidget(forms.MultiWidget):
    """ Виджет для отображения полей для ввода диапазона значений. """
    def __init__(self, attrs=None, **kwargs):
        widgets = (
            forms.TextInput(),
            forms.TextInput(),
            )
        #super(MinMaxWidget, self).__init__(widgets, {'id': 'desc'})
        super(MinMaxWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return (value[0], value[1])
        return (0, 0)

class MinMaxFormField(forms.MultiValueField):
    widget = MinMaxWidget

    def __init__(self, *args, **kwargs):
        fields = (
            forms.CharField(required=False),
            forms.CharField(required=False),
            )
        super(MinMaxFormField, self).__init__(fields, *args, **kwargs)

    def clean(self, data_list):
        if int(data_list[0]) > int(data_list[1]):
            raise forms.ValidationError(_(u'Min field is greater than Max field.'))

    def compress(self, data_list):
        if data_list:
            return data_list
        return None

class SearchFormMetaclass(ModelFormMetaclass):
    """ Данный метакласс предназначен для преобразования списка полей для
    реализации подстраивающихся поисковых форм. """

    def __new__(cls, name, bases, attrs):
        """ Метод для управления настройкой класса. """
        # вызываем метод родительского класса, получаем поля в base_fields
        new_class = super(SearchFormMetaclass, cls).__new__(cls, name, bases, attrs)
        #print new_class.base_fields

        new_base_fields = []

        # обрабатываем каждое поле
        for field_name in new_class.base_fields.keys():
            # получаем имя класса для поля
            field_class_name = type(new_class.base_fields[field_name]).__name__

            if field_class_name == 'IntegerField':
                #print 'создать диапазон для %s' % field_name
                new_base_fields.append((field_name, MinMaxFormField()))
                #new_base_fields.append(('%s_min' % field_name, IntegerField()))
                #new_base_fields.append(('%s_max' % field_name, IntegerField()))
            else:
                #print 'поле %s, класс %s' % (field_name, field_class_name)
                new_base_fields.append((field_name, new_class.base_fields[field_name]))

        # замещаем поля
        new_class.base_fields = SortedDict(new_base_fields)

        # вернуть настроенный класс
        return new_class

class BaseSearchForm(forms.ModelForm): # Lamp
    __metaclass__ = SearchFormMetaclass

    userinput = forms.CharField(max_length=10, required=False)
    simple = forms.BooleanField(widget=forms.HiddenInput, initial=False)

    def search(self):
        #print '== searching =='
        #print self.cleaned_data

        queryset = self._meta.model._default_manager.get_query_set()
        for item in self.fields:
            if isinstance(self.fields[item], MinMaxFormField):
                filter = {'%s__range' % item: self.cleaned_data[item]}
                queryset = queryset.filter(**filter)
        return queryset

class FullSearchForm(BaseSearchForm):
    class Meta:
        model = models.Lamp
        exclude = ('item',)

ipp_settings = settings.SHOP_ITEMS_PER_PAGE
ITEMS_PER_PAGE_CHOICE = [(1, ipp_settings),
                         (2, int(1.5 * ipp_settings)),
                         (3, int(2 * ipp_settings)),
                         (4, int(3 * ipp_settings))]
class SearchForm(forms.Form):
    """ Реализация формы простого поиска. """
    userinput = forms.CharField(max_length=64, required=False)
    howmuch = forms.ChoiceField(choices=ITEMS_PER_PAGE_CHOICE)
    simple = forms.BooleanField(widget=forms.HiddenInput, initial=True)

