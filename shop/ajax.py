# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
from cargo.shop import models, common

def show_count(request):
    """
    Функция получения количества товара на складе
    """
    if (request.is_ajax()):
        id = request.GET.get('item_id', 0)
        if id > 0:
            item = models.Item.objects.get(id=id)
            return HttpResponse('<result><code>200</code><desc>success</desc>' +
                                '<remains>%i</remains></result>' % (int(item.count) - int(item.reserved)),
                                mimetype="text/xml")
        else:
            return HttpResponse('<result><code>300</code><desc>bad id</desc></result>', mimetype="text/xml")
    else:
        return HttpResponse('<result><code>400</code><desc>it must be ajax call</desc></result>', mimetype="text/xml")

def add_to_cart(request):
    """
    Функция добавления товара в корзину.
    """
    if (request.is_ajax()):
        id = request.POST.get('item_id', 0)
        cnt = int(request.POST.get('item_count', 0))
        # проверить количество
        if id == 0 or cnt == 0:
            return HttpResponse('<result><code>302</code><desc>wrong parameters</desc></result>',
                                mimetype="text/xml")
        # инициализация корзины
        if not 'cart_items' in request.session:
            common.does_cart_exist(request)
        item = models.Item.objects.get(id=id)
        if (int(item.count) - int(item.reserved)) < cnt:
            return HttpResponse('<result><code>201</code><desc>not enough items</desc>' +
                                '<cart_count>%s</cart_count><cart_price>%s</cart_price></result>'
                                % (request.session['cart_count'], request.session['cart_price']),
                                mimetype="text/xml")
        else:
            # зарезервировать товар
            item.reserved += cnt
            item.save()
            # добавить информацию о товаре в сессию
            price = item.price
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
                request.session['cart_price'] += int(items[i]['count']) * float(models.Item.objects.get(id=i).price)
            # поместить в сессию
            request.session['cart_items'] = items
            return HttpResponse('<result><code>200</code><desc>success</desc>' +
                                '<cart_count>%s</cart_count><cart_price>%s</cart_price><remains>%s</remains></result>'
                                % (request.session['cart_count'], request.session['cart_price'], int(item.count) - int(item.reserved)),
                                mimetype="text/xml")
    else:
        return HttpResponse('<result><code>400</code><desc>it must be ajax call</desc></result>', mimetype="text/xml")

def clean_cart(request):
    """
    Функция очистки корзины
    """
    if (request.is_ajax()):
        items = request.session.get('cart_items', {})
        for i in items:
            dbitem = models.Item.objects.get(id=i)
            count = items[i].get('count', 0)
            if dbitem.reserved > 0:
                dbitem.reserved -= count
                dbitem.save()
        common.init_cart(request)
        return HttpResponse('<result><code>200</code><desc>done</desc></result>', mimetype="text/xml")
    else:
        return HttpResponse('<result><code>400</code><desc>it must be ajax call</desc></result>', mimetype="text/xml")

