# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect

from moiluchru.snippets import ajax_processor
from moiluchru.shop import common
from moiluchru.shop.forms import CartAdd, CartClean, CartRecalculate, CartRemoveItem
from moiluchru.shop.models import Item

@ajax_processor(CartAdd)
def add_to_cart(request, form):
    """ Функция добавления товара в корзину. """
    id = int(form.cleaned_data['item'])
    cnt = int(form.cleaned_data['count'])
    # инициализация корзины
    if not 'cart_items' in request.session:
        common.does_cart_exist(request)

    try:
        item = Item.objects.get(id=id)
        # добавить информацию о товаре в сессию
        price = item.get_price()[1]
        items = request.session.get('cart_items', {})
        if not id in items:
            items[id] = {}
        items[id]['count'] = int(items[id].get('count', 0)) + cnt
        items[id]['price'] = price
        # пересчитываем корзину
        request.session['cart_count'] = 0
        request.session['cart_price'] = 0.00
        for i in items:
            request.session['cart_count'] += int(items[i]['count'])
            request.session['cart_price'] += int(items[i]['count']) * float(Item.objects.get(id=i).get_price()[1])
        # поместить в сессию
        request.session['cart_items'] = items
        return {'code': '200', 'desc': 'success',
                'cart_count': request.session['cart_count'],
                'cart_price': request.session['cart_price']}
        
    except Item.DoesNotExists:
        return {'code': '300', 'desc': 'Can\'t get object'}

@ajax_processor(CartClean)
def clean_cart(request, form):
    """ Функция очистки корзины  """
    common.init_cart(request)
    return {'code': '200', 'desc': 'success'}

@ajax_processor(CartRecalculate)
def cart_recalculate(request, form):
    """ Функция пересчёта корзины  """
    common.init_cart(request)

    
    return {'code': '200', 'desc': 'success'}

