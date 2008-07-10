# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.utils.translation import ugettext, gettext_lazy as _
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.core import validators
from django import newforms as forms
from django.contrib import auth
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin import models as admmodels
from cargo.shop import models

def is_stuff(user):
    return user.is_authenticated()

def login(request):
    """
    Функция для отображения страницы для ввода логина.
    """
    # Класс для формы логина
    class LoginForm(forms.Form):
        login = forms.CharField(label=ugettext('Login'), max_length=30,
                                widget=forms.TextInput(attrs={'class':'longitem wideitem'}))
        passwd = forms.CharField(label=ugettext('Password'), max_length=128,
                                 widget=forms.PasswordInput(attrs={'class':'longitem wideitem'}))

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            try:
                login = request.POST['login']
                passwd = request.POST['passwd']
                user = auth.authenticate(username=login, password=passwd)
                if user is not None and user.is_active:
                    auth.login(request, user)
                    return HttpResponseRedirect("/shop/orders/active/")
                else:
                    return render_to_response('manager-login.html',
                                              {'form': form, 'panel_hide': 'yes',
                                               'login_error': 'Возможно, вы неправильно указали данные.'})
                    return HttpResponseRedirect("/shop/manager/")
            except Exception:
                return HttpResponse('bad form data')
        else:
            return HttpResponse('bad form')
    else:
        if not request.session.test_cookie_worked():
            request.session.set_test_cookie()
        form = LoginForm(auto_id='field_%s')
        return render_to_response('manager-login.html',
                                  {'user': request.user, 'form': form, 'panel_hide': 'yes'})

@user_passes_test(is_stuff, login_url="/shop/manager/")
def logout(request):
    """
    Представление для осуществления выхода из административной части.
    """
    auth.logout(request)
    return HttpResponseRedirect('/shop/')
    
@user_passes_test(is_stuff, login_url="/shop/manager/")
def orders(request, act):
    """
    Представление для отображения активных заказов.
    """
    if act == 'active': status = 1
    orders = models.Order.objects.filter(status=status)
    return render_to_response('manager-orders.html', {'orders': orders,
                                                      'user': request.user})

@user_passes_test(is_stuff, login_url="/shop/manager/")
def order_info(request, order_id):
    """
    Представление для отображения полной информации о заказе.
    """
    # Класс предназначен для переопределения метода отображения списка курьеров
    class CourierSelect(forms.ModelChoiceField):
        def label_from_instance(self, obj):
            return "%s" % obj.get_full_name()
            
    class OrderForm(forms.Form):
        status = forms.ModelChoiceField(queryset=models.OrderStatus.objects.all(),
                                        label=ugettext('Status'),
                                        widget=forms.Select(attrs={'class':'longitem wideitem'}))
        courier = CourierSelect(queryset=admmodels.User.objects.filter(groups=1),
                                label=ugettext('Courier'),
                                widget=forms.Select(attrs={'class':'longitem wideitem'}))
        
    class CartItem:
        def __init__(self, title, count, price):
            self.title = title
            self.count = count
            self.price = price
            self.cost = count * price

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # обработать форму
            try:
                pass
            except Exception:
                return HttpResponse('bad form data')
        else:
            return HttpResponse('bad form')
    else:
        items = []
        o = models.Order.objects.get(id=order_id)
        p = models.Phone.objects.get(owner=o.buyer)
        d = models.OrderDetail.objects.filter(order=order_id)
        for i in d:
            items.append(CartItem(i, i.count, i.price))
        form = OrderForm(auto_id='field_%s', initial={'status': o.status.id})
        return render_to_response('manager-orderinfo.html',
                                  {'form': form, 'order': o, 'phone': p, 'items': items,
                                   'user_full_name': request.user.first_name})
