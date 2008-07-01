# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.utils.translation import ugettext, gettext_lazy as _
from django.http import HttpResponse
from django.core import validators
from cargo.shop.models import Category, Producer, Item

def show_main_page(request):
    """
    Функция для отображения главной страницы сайта.
    Осуществляем проверку поддержки Cookie.
    """
    if not request.session.test_cookie_worked():
        request.session.set_test_cookie()
    else:
        does_cart_exist(request)
    return render_to_response('shop-show-main.html',
                              {'queryset': Category.objects.filter(parent__isnull=True)[:5],
                               'cart_count': request.session.get('cart_count', 0),
                               'cart_price': request.session.get('cart_price', 0.00)
                               })
    
def show_category_page(request, category):
    """
    Функция для отображения подчинённых категорий.
    """
    does_cart_exist(request)
    c = Category.objects.get(id=category)
    return render_to_response('shop-show-category.html',
                              {'parent_cats': get_parent_cats(c),
                               'categories': c.category_set.all(),
                               'producers': get_currcat_procs(c),
                               'items': get_currcat_items(category),
                               'cart_count': request.session.get('cart_count', 0),
                               'cart_price': request.session.get('cart_price', 0.00)
                               })

def show_item_page(request, item):
    does_cart_exist(request)
    curr_item = Item.objects.get(id=item)
    return render_to_response('shop-show-item.html',
                              {'item': curr_item,
                               'parent_cats': get_parent_cats(curr_item.category),
                               'cart_count': request.session.get('cart_count', 0),
                               'cart_price': request.session.get('cart_price', 0.00)
                               })
    
def does_cart_exist(request):
    if request.session.test_cookie_worked():
        if not 'cart' in request.session:
            init_cart(request)
    else:
        raise validators.ValidationError("Your Web browser doesn't appear " +
                                         "to have cookies enabled. " +
                                         "Cookies are required for logging in.")

def init_cart(request):
    request.session['cart_items'] = {}
    request.session['cart_count'] = 0
    request.session['cart_price'] = 0.00

def add_to_cart(request):
    """
    Функция добавления товара в корзину.
    """
    if (request.is_ajax()):
        id = request.POST.get('item_id', 0)
        cnt = request.POST.get('item_count', 0)
#         id = request.GET.get('item_id', 0)
#         cnt = request.GET.get('item_count', 0)
        #  return HttpResponse('<result>error<id>%s</id><count>%s</count></result>' % (id, cnt), mimetype="text/xml")
        # проверить количество
        if id == 0 or cnt == 0:
            return HttpResponse('<result>error 1</result>', mimetype="text/xml")
        # инициализация корзины
        if not 'cart_items' in request.session:
            does_cart_exist(request)
        # добавить информацию о товаре в сессию
        price = Item.objects.get(id=id).price
        items = request.session.get('cart_items', {})
        if not id in items:
            items[id] = {}
        items[id]['count'] = int(items[id].get('count', 0)) + int(cnt)
        items[id]['price'] = price
        # пересчитываем корзину
        request.session['cart_count'] = 0
        request.session['cart_price'] = 0.00
        for i in items:
            request.session['cart_count'] += int(items[i]['count'])
            request.session['cart_price'] += int(items[i]['count']) * float(Item.objects.get(id=i).price)
        # поместить в сессию
        request.session['cart_items'] = items
        return HttpResponse('<result><text>ok</text><cart_count>%s</cart_count><cart_price>%s</cart_price></result>'
                            % (request.session['cart_count'], request.session['cart_price']),
                            mimetype="text/xml")
    else:
        return HttpResponse('<result><text>error</text></result>', mimetype="text/xml")

def clean_cart(request):
    """
    Функция очистки корзины
    """
    if (request.is_ajax()):
        init_cart(request)
        return HttpResponse('<result>ok</result>', mimetype="text/xml")
    else:
        return HttpResponse('<result>error 2</result>', mimetype="text/xml")

def get_parent_cats(category):
    """
    Выборка с помощью метода select_related() получает из БД все
    связанные категории, но возвращается только указанная, которая
    и помещается в массив. Далее вся работа идёт с кэшем, БД здесь
    больше не используется. НО ЧТО-ТО НЕ ЗАХОТЕЛО РАБОТАТЬ :(
    """
    #a = [Category.objects.select_related().get(id=category)]
    a = [category]
    curcat = category
    while True:
        if curcat.parent:
            a.insert(0, curcat.parent)
            curcat = curcat.parent
        else:
            break
    return a

# def gg(c):
#     a = [c]
#     return a + [gg(c.parent) if c.parent]

def get_sub_cats(category):
    """Функция возвращает все дочерние категории,
    даже дочерние дочерних и так далее."""
    result = list(category.category_set.all())
    return reduce(lambda a,b: a + b,
                  [get_sub_cats(l) for l in result],
                  result)

def get_currcat_items(category):
    """Функция возвращает элементы текущей категории."""
    return Item.objects.filter(category=category)

def get_currcat_procs(category):
    """Функция возвращает производителей текущей категории."""
    return [l.producer for l in get_currcat_items(category)]
    
def get_sub_cats_items(category):
    """Функция возвращает элементы всех дочерних категорий,
    включая указанную."""
    cats = set(get_sub_cats(category))
    return Item.objects.filter(category__in=cats)
