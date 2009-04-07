# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.utils.translation import ugettext, gettext_lazy as _
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.core.paginator import Paginator
from django.contrib import auth
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin import models as admmodels

from moiluchru import settings
from moiluchru.shop import models
from moiluchru.shop.forms import DivErrorList, CourierSelect, LoginForm, OrderForm
from moiluchru.shop.classes import CartItem

def is_stuff(user):
    return user.is_authenticated()

def ctx_processor(request):
    """ Контекстный процессор. """
    return {'site_name': settings.SITE_NAME,
            'user': request.user}

def login(request):
    """ Функция для отображения страницы для ввода логина. """
    if is_stuff(request.user):
        return HttpResponseRedirect("/shop/orders/all/")

    if request.session.test_cookie_worked():
        #request.session.delete_test_cookie()

        if request.method == 'POST':
            form = LoginForm(request.POST)
            if form.is_valid():
                try:
		    # TODO: это некошерно, надо использовать cleaned_data
                    login = request.POST['login']
                    passwd = request.POST['passwd']
                    user = auth.authenticate(username=login, password=passwd)
                    if user is not None and user.is_active:
                        auth.login(request, user)
                        return HttpResponseRedirect("/shop/orders/all/")
                    else:
                        return render_to_response('shop/manager/login.html',
                                                  {'form': form, 'panel_hide': 'yes',
                                                   'login_error': 'Возможно, вы неправильно указали данные.'})
                except Exception:
                    return HttpResponse('bad form data')
            else:
                return HttpResponse('bad form')
        else:
            form = LoginForm(auto_id='field_%s')
            return render_to_response('shop/manager/login.html',
                                      {'form': form, 'panel_hide': 'yes'},
                                      context_instance=RequestContext(request, processors=[ctx_processor]))
    else:
        request.session.set_test_cookie()
        return HttpResponseRedirect("/shop/manager/")

@user_passes_test(is_stuff, login_url="/shop/manager/")
def logout(request):
    """ Представление для осуществления выхода из административной части.  """
    auth.logout(request)
    return HttpResponseRedirect('/shop/')
    
@user_passes_test(is_stuff, login_url="/shop/manager/")
def orders(request, act, page=1):
    """ Представление для отображения активных заказов. """
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
    p = Paginator(orders, settings.MANAGER_ORDERS_PER_PAGE)
    return render_to_response('shop/manager/orders.html', {'orders': p.page(page).object_list,
                                                      'page': p.page(page), 'page_range': p.page_range,
                                                      'url': '/shop/orders/%s/' % act},
                              context_instance=RequestContext(request, processors=[ctx_processor]))

@user_passes_test(is_stuff, login_url="/shop/manager/")
def order_info(request, order_id):
    """ Представление для отображения полной информации о заказе.  """
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
            return render_to_response('shop/manager/orderinfo.html',
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
        return render_to_response('shop/manager/orderinfo.html',
                                  {'form': form, 'order': o, 'phone': p, 'items': items, 'history': history},
                                  context_instance=RequestContext(request, processors=[ctx_processor]))
