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
    courier = CourierSelect(label=_(u'Courier'), required=False,
                            queryset=admmodels.User.objects.filter(groups=1),
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
        super(MinMaxWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return (value[0], value[1])
        return (0, 0)

class MinMaxFormField(forms.MultiValueField):
    """ Поле формы, обеспечивающее ввод диапазона. """
    widget = MinMaxWidget

    def __init__(self, *args, **kwargs):
        fields = (
            # required=False автоматически назначается в родительском конструкторе
            forms.CharField(),
            forms.CharField(),
            )
        super(MinMaxFormField, self).__init__(fields, *args, **kwargs)

    def clean(self, data_list):
        if int(data_list[0]) > int(data_list[1]):
            raise forms.ValidationError(_(u'Min field is greater than Max field.'))
        return data_list

    def compress(self, data_list):
        return data_list

class SearchFormMetaclass(ModelFormMetaclass):
    """ Данный метакласс предназначен для преобразования списка полей для
    реализации подстраивающихся поисковых форм. """

    def __new__(cls, name, bases, attrs):
        """ Метод для управления настройкой класса. """
        # вызываем метод родительского класса, получаем поля в base_fields
        new_class = super(SearchFormMetaclass, cls).__new__(cls, name, bases, attrs)

        new_base_fields = []

        # обрабатываем каждое поле
        for field_name in new_class.base_fields.keys():
            fobj = new_class.base_fields[field_name]
            # получаем имя класса для поля
            field_class_name = type(fobj).__name__

            if field_class_name in ['IntegerField', 'FloatField']:
                widget = MinMaxFormField()
                widget.label = fobj.label
                widget.help_text = fobj.help_text
                new_base_fields.append((field_name, widget))
            else:
                # в полном поиске ни одно поле не может быть обязательным
                new_class.base_fields[field_name].required = False
                new_base_fields.append((field_name, fobj))

        # замещаем поля
        new_class.base_fields = SortedDict(new_base_fields)

        # вернуть настроенный класс
        return new_class

# Настройки для выпадашки "количество элементов на странице".
ipp_settings = settings.SHOP_ITEMS_PER_PAGE
ITEMS_PER_PAGE_CHOICE = [(1, ipp_settings),
                         (2, int(1.5 * ipp_settings)),
                         (3, int(2 * ipp_settings)),
                         (4, int(3 * ipp_settings))]

class BaseSearchForm(forms.ModelForm):
    """ Базовый класс для форм, строящихся по модели. """
    __metaclass__ = SearchFormMetaclass

    simple = forms.BooleanField(widget=forms.HiddenInput, 
                                initial=False, required=False)

    def search(self):
        queryset = self._meta.model._default_manager.get_query_set()
        for item in self.fields:
            # обработка специального поля
            if item == 'simple':
                continue
            # получаем значение и соответственно обрабатываем его
            value = self.cleaned_data[item]
            if isinstance(self.fields[item], forms.BooleanField):
                queryset = queryset.filter(**{'%s' % item: value})
            if isinstance(self.fields[item], forms.ModelChoiceField):
                if value is None:
                    continue
                queryset = queryset.filter(**{'%s' % item: value})
            if isinstance(self.fields[item], MinMaxFormField):
                # обработка ситуации по умолчанию: оба поля равны нулю
                (min, max) = value
                if int(min) == int(max) and int(max) == 0:
                    continue
                # фильтруем набор по диапазону
                filter = {'%s__range' % item: value}
                queryset = queryset.filter(**filter)
        return queryset

class SearchForm(forms.Form):
    """ Реализация формы простого поиска. """
    userinput = forms.CharField(max_length=64, required=False)
    howmuch = forms.ChoiceField(choices=ITEMS_PER_PAGE_CHOICE)
    simple = forms.BooleanField(widget=forms.HiddenInput, 
                                initial=True, required=False)

def modelform_factory(model, form=BaseSearchForm, fields=None, exclude=None,
                       formfield_callback=lambda f: f.formfield()):
    # Create the inner Meta class. FIXME: ideally, we should be able to
    # construct a ModelForm without creating and passing in a temporary
    # inner class.

    # Build up a list of attributes that the Meta object will have.
    attrs = {'model': model}
    if fields is not None:
        attrs['fields'] = fields
    if exclude is not None:
        attrs['exclude'] = exclude

    # If parent form class already has an inner Meta, the Meta we're
    # creating needs to inherit from the parent's inner meta.
    parent = (object,)
    if hasattr(form, 'Meta'):
        parent = (form.Meta, object)
    Meta = type('Meta', parent, attrs)

    # Give this new form class a reasonable name.
    class_name = model.__name__ + 'Form'

    # Class attributes for the new form class.
    form_class_attrs = {
        'Meta': Meta,
        'formfield_callback': formfield_callback
    }

    return SearchFormMetaclass(class_name, (form,), form_class_attrs)

def get_search_form(form_dict, initial=None, data=None):
    form_class = modelform_factory(form_dict['model'], exclude=form_dict['exclude'])
    return form_class(data=data, initial=initial)

