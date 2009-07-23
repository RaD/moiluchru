# -*- coding: utf-8 -*-

from django.conf import settings

from snippets import ajax_processor
from shop import common
from shop.forms import CartAdd, CartClean, CartRecalculate, CartRemoveItem
from shop.models import Item
from jabber.forms import JabberMessage
from jabber.models import Message

from datetime import timedelta, datetime as dt

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
    if 'system' in form.cleaned_data and form.cleaned_data['system'] == '1': # системное сообщение
        # отправляем сообщение сервису для закрытия соединения
        try:
            nick = request.session['JABBER_NICK']
            msg = Message(nick=nick, msg='close connection', is_system=True)
            msg.save()
            # удаляем информацию из сессии
            del(request.session['JABBER_NICK'])
        except KeyError:
            # нет такого ключа, значит ничего не делаем
            pass

        return {'code': '200', 'desc': 'closed'} # FIXME

    # при первом обращении клиента следует автоматически сгенерировать
    # ему ник из минут и секунд, ник записывается в сессию и
    # используется при дальнейшем общении, на сессию накладывается
    # получасовое ограничение времени жизни после последнего
    # сообщения.
    now = dt.now()
    last = request.session.get('JABBER_LAST', now - timedelta(days=1))
    if now - timedelta(minutes=30) > last and 'JABBER_NICK' in request.session:
        # отправляем сообщение сервису для закрытия соединения
        nick = request.session['JABBER_NICK']
        msg = Message(nick=nick, msg='close connection', is_system=True)
        msg.save()
        # удаляем информацию из сессии
        del(request.session['JABBER_NICK'])

    nick = request.session.get('JABBER_NICK', dt.now().strftime('%M%S'))
    
    try:
        message = form.cleaned_data['message'] # может быть пустым
        msg = Message(nick=nick, msg=message)
        msg.save()
        request.session['JABBER_NICK'] = nick
        request.session['JABBER_LAST'] = dt.now()
    except Exception, e:
        return {'code': '400', 'desc': e}
    return {'code': '200', 'desc': 'sent'}

# Отправка сообщения клиенту
@ajax_processor(None)
def jabber_poll(request):
    nick = request.session.get('JABBER_NICK', dt.now().strftime('%M%S'))
    try:
        # приём сообщений
        msgs = Message.objects.filter(nick=nick, is_processed=False, client_admin=False).order_by('sent_date')
        for m in msgs:
            m.is_processed = True
            m.save()
    except Exception, e:
        return {'code': '400', 'desc': e}
    return {'code': '200', 'desc': 'done', 'messages': [m.msg for m in msgs]}
