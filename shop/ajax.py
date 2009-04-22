# -*- coding: utf-8 -*-

from django.conf import settings
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
        # поместить в сессию
        request.session['cart_items'] = items
        
        request.session['cart_count'] = 0
        request.session['cart_price'] = 0.00
        for i in request.session.get('cart_items', {}):
            request.session['cart_count'] += int(items[i]['count'])
            request.session['cart_price'] += int(items[i]['count']) * float(Item.objects.get(id=i).get_price()[1])
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

#@ajax_processor(None)
def cart_recalculate(request, form=None):
    """ Функция пересчёта корзины  """
    from django.utils import simplejson
    import pdb; pdb.set_trace()
    items = request.POST.get('items')
    print type(items)
    print items
    print simplejson.loads(items, encoding=settings.DEFAULT_CHARSET)
    return {'code': '200', 'desc': 'success'}
#             try:
#                 item = Item.objects.get(id=id)
#                 price = item.get_price()[1]
#                 if not id in items:
#                     items[id] = {}
#                 items[id]['count'] = int(items[id].get('count', 0)) + cnt
#                 items[id]['price'] = price


#             items = 
#         request.session['cart_items'] = items
#         return {'code': '200', 'desc': 'success'}
#     else:
    
    

    

@ajax_processor(CartRemoveItem)
def cart_remove_item(request, form):
    id = int(form.cleaned_data['item'])
    items = request.session['cart_items']
    del(items[id])
    request.session['cart_items'] = items
    request.session['cart_count'] = 0
    request.session['cart_price'] = 0.00
    for i in request.session.get('cart_items', {}):
        request.session['cart_count'] += int(items[i]['count'])
        request.session['cart_price'] += int(items[i]['count']) * float(Item.objects.get(id=i).get_price()[1])
    return {'code': '200', 'desc': 'success',
            'cart_count': request.session['cart_count'],
            'cart_price': request.session['cart_price']}
