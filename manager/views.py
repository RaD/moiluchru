# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin.models import User
from django.core.paginator import Paginator
from django.forms import ValidationError
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import gettext_lazy as _

from moiluchru.snippets import render_to, paged
from moiluchru.shop.models import Order, OrderDetail, OrderStatus, OrderStatusChange, Phone
from moiluchru.shop.forms import DivErrorList, CourierSelect, LoginForm, OrderForm
from moiluchru.shop.classes import CartItem

def is_stuff(user):
    return user.is_authenticated()

def ctx_processor(request):
    """ Контекстный процессор. """
    return {'site_name': settings.SITE_NAME,
            'user': request.user}

@render_to('manager/login.html', ctx_processor)
def login(request):
    """ Функция для отображения страницы для ввода логина. """
    if is_stuff(request.user):
        return HttpResponseRedirect("/manager/orders/all/")

    if request.session.test_cookie_worked():
        #request.session.delete_test_cookie()

        if request.method == 'POST':
            form = LoginForm(request.POST)
            if form.is_valid():
                try:
                    login = form.cleaned_data.get('login', None)
                    passwd = form.cleaned_data.get('passwd', None)
                    user = auth.authenticate(username=login, password=passwd)
                    if user and passwd and user.is_active:
                        auth.login(request, user)
                        return HttpResponseRedirect("/manager/orders/all/")
                    else:
                        return {'form': form, 'panel_hide': 'yes',
                                'login_error': 'Возможно, вы неправильно указали данные.'}
                except Exception:
                    request.session['error'] = _(u'Form has bad data.')
                    raise ValidationError
            else:
                request.session['error'] = _(u'Form has bad data.')
                raise ValidationError
        else:
            form = LoginForm(auto_id='field_%s')
            return {'form': form, 'panel_hide': 'yes'}
    else:
        request.session.set_test_cookie()
        return HttpResponseRedirect("/manager/")

@user_passes_test(is_stuff, login_url="/manager/")
def logout(request):
    """ Представление для осуществления выхода из административной части.  """
    auth.logout(request)
    return HttpResponseRedirect('/shop/')
    
@user_passes_test(is_stuff, login_url="/manager/")
@render_to('manager/orders.html', ctx_processor)
def orders(request, act, page=1):
    """ Представление для отображения активных заказов. """
    try:
        orders = Order.objects.all()
        actions = {'waiting': 1, 'confirmed': 2, 'delivered': 3, 'canceled': 4, 'impossible': 5}
        if act != 'all': orders = orders.filter(status=actions[act])
        orders = orders.order_by('-id')
    except Order.DoesNotExist:
        pass # FIXME
    p = Paginator(orders, settings.MANAGER_ORDERS_PER_PAGE)
    return {'orders': p.page(page).object_list,
            'page': p.page(page), 'page_range': p.page_range,
            'url': '/manager/orders/%s/' % act}

@user_passes_test(is_stuff, login_url="/manager/")
@render_to('manager/orderinfo.html', ctx_processor)
def order_info(request, order_id):
    """ Представление для отображения полной информации о заказе.  """
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # обработать форму
            try:
                c = form.cleaned_data
                courier = c.get('courier', None)
                status = c.get('status')
                order = Order.objects.get(id=order_id)
                if order.status != status or order.courier != courier:
                    change = OrderStatusChange(
                        order = order, old_status = order.status,
                        new_status = status, courier = courier)
                    change.save()
                    order.courier = courier
                    order.status = status
                order.save()
                return HttpResponseRedirect('/manager/orderinfo/%i' % int(order_id))
            except User.DoesNotExist:
                request.session['error'] = 'User does not exist.'
            except Order.DoesNotExist:
                request.session['error'] = 'Order does not exist.'
            except OrderStatus.DoesNotExist:
                request.session['error'] = 'Order status does not exist.'
            except Exception, e:
                request.session['error'] = e
            return HttpResponseRedirect('/manager/error/')
        else:
            o = Order.objects.get(id=order_id)
            p = Phone.objects.get(owner=o.buyer)
            d = OrderDetail.objects.filter(order=order_id)
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
            history = OrderStatusChange.objects.filter(order=order_id).order_by('-reg_date')
            return {'form': form, 'order': o, 'phone': p, 'items': items, 'history': history }
    else:
        o = Order.objects.get(id=order_id)
        p = Phone.objects.get(owner=o.buyer)
        d = OrderDetail.objects.filter(order=order_id)
        if o.courier:
            courier = o.courier.id
        else:
            courier = 0
        form = OrderForm(auto_id='field_%s', initial={'status': o.status.id, 'courier': courier})
        # корзина
        items = []
        for i in d:
            items.append(CartItem(i, i.count, i.price))
        # история
        history = OrderStatusChange.objects.filter(order=order_id).order_by('-reg_date')
        return {'form': form, 'order': o, 'phone': p, 'items': items, 'history': history}

@user_passes_test(is_stuff, login_url="/manager/")
def error(request):
    return HttpResponse(request.session['error'])
