# -*- coding: utf-8 -*-

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse

from django.contrib import auth
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin.models import User
from django.forms import ValidationError
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import ugettext_lazy as _

from snippets import render_to, paginate_by
from manager.forms import OrderForm, DiscountForm
from shop.models import Order, OrderDetail, OrderStatus, OrderStatusChange, Phone
from shop.forms import LoginForm
from shop.views import CartItem

def is_stuff(user):
    return user.is_authenticated()

def ctx_processor(request):
    """ Контекстный процессор. """
    return {'site_name': settings.SITE_TITLE,
            'user': request.user}

@render_to('manager/login.html', ctx_processor)
def login(request):
    """ Функция для отображения страницы для ввода логина. """
    if is_stuff(request.user):
        return HttpResponseRedirect(reverse('orders', args=['all']))

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
                        return HttpResponseRedirect(reverse('orders', args=['all']))
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
        return HttpResponseRedirect(reverse('index'))

@user_passes_test(is_stuff, login_url="/manager/")
def logout(request):
    """ Представление для осуществления выхода из административной части.  """
    auth.logout(request)
    return HttpResponseRedirect('/')
    
@user_passes_test(is_stuff, login_url="/manager/")
@render_to('manager/orders.html', ctx_processor)
@paginate_by('orders')
def orders(request, act):
    """ Представление для отображения активных заказов. """
    try:
        orders = Order.objects.all()
        actions = {'waiting': 1, 'confirmed': 2, 'delivered': 3, 'canceled': 4, 'impossible': 5}
        if act != 'all': orders = orders.filter(status=actions[act])
        orders = orders.order_by('-id')

        def set_discount_price(order):
            order.discountprice = order.totalprice - (order.totalprice / 100 * order.discount)
            return order
        orders = map(set_discount_price, orders)
    except Order.DoesNotExist:
        pass # FIXME
    return {'orders': orders,
            'url': reverse('orders', args=[act])
            }

@user_passes_test(is_stuff, login_url="/manager/")
@render_to('manager/orderinfo.html', ctx_processor)
def order_info(request, order_id):
    """ Представление для отображения полной информации о заказе.  """
    order = get_object_or_404(Order, id__exact=order_id)
    order.discountprice = order.totalprice - (order.totalprice / 100 * order.discount)
    history = order.orderstatuschange_set.order_by('-reg_date')
    phone = Phone.objects.filter(owner=order.buyer)[0] # FIXME
    try:
        courier = order.courier.id
    except:
        courier = 0

    # корзина
    items = []
    for i in order.orderdetail_set.all():
        items.append(CartItem(i.item, i.count, i.price))
    
    forms_list = []
    for (form_class, initial) in [(DiscountForm, {'discount': order.discount}),
                                   (OrderForm, {'status': order.status.id, 'courier': courier})]:
        form = form_class(request.POST or None, order=order)
        if request.method == 'POST' and form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('orderinfo', args=[order.id]))
        else:
            form = form_class(initial=initial)
            forms_list.append(form)
    return {'forms': forms_list, 
            'order': order, 'phone': phone, 'items': items, 'history': history}
        
@user_passes_test(is_stuff, login_url="/manager/")
def error(request):
    return HttpResponse(request.session['error'])
