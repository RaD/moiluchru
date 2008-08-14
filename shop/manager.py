# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.utils.translation import ugettext, gettext_lazy as _
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.core import validators
from django import newforms as forms
from django.newforms.util import ErrorList
from django.contrib import auth
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin import models as admmodels
from cargo import settings
from cargo.shop import models

def is_stuff(user):
    return user.is_authenticated()

def ctx_processor(request):
    """ Контекстный процессор. """
    return {'site_name': settings.SITE_NAME,
            'user': request.user}

def login(request):
    """
    Функция для отображения страницы для ввода логина.
    """
    if is_stuff(request.user):
        return HttpResponseRedirect("/shop/orders/all/")

    # Класс для формы логина
    class LoginForm(forms.Form):
        login = forms.CharField(label=ugettext('Login'), max_length=30,
                                widget=forms.TextInput(attrs={'class':'longitem'}))
        passwd = forms.CharField(label=ugettext('Password'), max_length=128,
                                 widget=forms.PasswordInput(attrs={'class':'longitem'}))

    if request.session.test_cookie_worked():
        #request.session.delete_test_cookie()

        if request.method == 'POST':
            form = LoginForm(request.POST)
            if form.is_valid():
                try:
                    login = request.POST['login']
                    passwd = request.POST['passwd']
                    user = auth.authenticate(username=login, password=passwd)
                    if user is not None and user.is_active:
                        auth.login(request, user)
                        return HttpResponseRedirect("/shop/orders/all/")
                    else:
                        return render_to_response('manager-login.html',
                                                  {'form': form, 'panel_hide': 'yes',
                                                   'login_error': 'Возможно, вы неправильно указали данные.'})
                except Exception:
                    return HttpResponse('bad form data')
            else:
                return HttpResponse('bad form')
        else:
            form = LoginForm(auto_id='field_%s')
            return render_to_response('manager-login.html',
                                      {'form': form, 'panel_hide': 'yes'},
                                      context_instance=RequestContext(request, processors=[ctx_processor]))
    else:
        request.session.set_test_cookie()
        return HttpResponseRedirect("/shop/manager/")

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
    if act == 'all':
        orders = models.Order.objects.all().order_by('-id')
    elif act == 'waiting': 
        orders = models.Order.objects.filter(status=1).order_by('-id')
    elif act == 'confirmed': 
        orders = models.Order.objects.filter(status=2).order_by('-id')
    elif act == 'delivered': 
        orders = models.Order.objects.filter(status=3).order_by('-id')
    elif act == 'canceled': 
        orders = models.Order.objects.filter(status=4).order_by('-id')
    elif act == 'impossible': 
        orders = models.Order.objects.filter(status=5).order_by('-id')
    return render_to_response('manager-orders.html', {'orders': orders},
                              context_instance=RequestContext(request, processors=[ctx_processor]))

@user_passes_test(is_stuff, login_url="/shop/manager/")
def order_info(request, order_id):
    """
    Представление для отображения полной информации о заказе.
    """
    # Класс предназначен для переопределения метода отображения списка курьеров
    class CourierSelect(forms.ModelChoiceField):
        def label_from_instance(self, obj):
            return "%s" % obj.get_full_name()
            
    # класс формы
    class OrderForm(forms.Form):
        status = forms.ModelChoiceField(queryset=models.OrderStatus.objects.all(),
                                        label=ugettext('Status'), 
                                        widget=forms.Select(attrs={'class':'longitem'}))
        courier = CourierSelect(queryset=admmodels.User.objects.filter(groups=1),
                                label=ugettext('Courier'),
                                widget=forms.Select(attrs={'class':'longitem'}))

    # Определяем класс для отображения ошибок в пользовательском вводе
    class DivErrorList(ErrorList):
        def __unicode__(self):
            return self.as_divs()
        def as_divs(self):
            if not self: return u''
            return u'<div class="errorlist">%s</div>' % ''.join([u'<div class="error">%s</div>' % e for e in self])
    # класс объекта
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
                courier = admmodels.User.objects.get(id=request.POST['courier'])
                status = models.OrderStatus.objects.get(id=request.POST['status'])
                order = models.Order.objects.get(id=order_id)
                if order.status != status or order.courier != courier:
                    change = models.OrderStatusChange(order = order,
                                                      old_status = order.status,
                                                      new_status = status,
                                                      courier = courier)
                    change.save()
                    order.courier = courier
                    order.status = status
                order.save()
                return HttpResponseRedirect('/shop/orderinfo/%i' % int(order_id))
            except Exception, e:
                return HttpResponse('bad form data: %s' % e)
        else:
            o = models.Order.objects.get(id=order_id)
            p = models.Phone.objects.get(owner=o.buyer)
            d = models.OrderDetail.objects.filter(order=order_id)
            if o.courier:
                courier = o.courier.id
            else:
                courier = 0
            form = OrderForm(request.POST, auto_id='field_%s', error_class=DivErrorList)
            # корзина
            items = []
            for i in d:
                items.append(CartItem(i, i.count, i.price))
            # история
            history = models.OrderStatusChange.objects.filter(order=order_id).order_by('-reg_time')
            return render_to_response('manager-orderinfo.html',
                                      {'form': form, 'order': o, 'phone': p, 'items': items, 'history': history },
                                      context_instance=RequestContext(request, processors=[ctx_processor]));
            return HttpResponse('bad form')
    else:
        o = models.Order.objects.get(id=order_id)
        p = models.Phone.objects.get(owner=o.buyer)
        d = models.OrderDetail.objects.filter(order=order_id)
        if o.courier:
            courier = o.courier.id
        else:
            courier = 0
        form = OrderForm(auto_id='field_%s', initial={'status': o.status.id,
                                                      'courier': courier})
        # корзина
        items = []
        for i in d:
            items.append(CartItem(i, i.count, i.price))
        # история
        history = models.OrderStatusChange.objects.filter(order=order_id).order_by('-reg_time')
        return render_to_response('manager-orderinfo.html',
                                  {'form': form, 'order': o, 'phone': p, 'items': items, 'history': history},
                                  context_instance=RequestContext(request, processors=[ctx_processor]))
