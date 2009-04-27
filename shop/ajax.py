# -*- coding: utf-8 -*-

import logging

from django.conf import settings

from moiluchru.snippets import ajax_processor
from moiluchru.shop import common
from moiluchru.shop.forms import CartAdd, CartClean, CartRecalculate, CartRemoveItem, JabberMessage
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

@ajax_processor(CartRecalculate)
def cart_recalculate(request, form):
    """ Функция пересчёта корзины  """
    id = int(form.cleaned_data['item'])
    count = int(form.cleaned_data['count'])
    item_total = count * float(Item.objects.get(id=id).get_price()[1])

    items = request.session.get('cart_items', {})
    items[id]['count'] = count

    request.session['cart_count'] = 0
    request.session['cart_price'] = 0.00
    for i in request.session.get('cart_items', {}):
        request.session['cart_count'] += int(items[i]['count'])
        request.session['cart_price'] += int(items[i]['count']) * float(Item.objects.get(id=i).get_price()[1])
    return {'code': '200', 'desc': 'success',
            'cart_count': request.session['cart_count'],
            'cart_price': '%.2f' % (request.session['cart_price'],),
            'item_total': '%.2f' % (item_total,)}

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

# Отправка сообщения на джаббер
@ajax_processor(JabberMessage)
def jabber_message(request, form):
    logger = logging.getLogger('moiluchrulogger')
    try:
        from moiluchru.shop.jabberclient import Client
        from pyxmpp.all import JID
    except ImportError:
        print 'jabber_message: Import error. Install pyxmpp!'
        logger.debug('jabber_message: Import error. Install pyxmpp!')

    action = form.cleaned_data['action']
    message = form.cleaned_data['message']

    import pdb; pdb.set_trace()
    logger.debug('%s: %s' % (action, message))
    if action == 'connect':
        c = Client(JID(settings.JABBER_ID),
                   settings.JABBER_PASSWORD)
        c.connect()
        return {'code': '200', 'sub': '1', 'desc': 'connected'}
    elif action == 'send':
        if not jid.resource:
            jid = JID(jid.node, jid.domain, 'CommBot [moiluch.ru]')
        return {'code': '200', 'sub': '2', 'desc': 'sent'}
    else:
        return {'code': '400', 'desc': 'error'}
