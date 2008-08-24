# -*- coding: utf-8 -*-
from django.core import validators
from cargo.shop import models

def init_cart(request):
    request.session['cart_items'] = {}
    request.session['cart_count'] = 0
    request.session['cart_price'] = 0.00

def does_cart_exist(request):
    if request.session.test_cookie_worked():
        if not 'cart_items' in request.session:
            init_cart(request)
    else:
        raise validators.ValidationError("Your Web browser doesn't appear " +
                                         "to have cookies enabled. " +
                                         "Cookies are required for logging in.")

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

def get_currcat_items(category, producer=None):
    """Функция возвращает элементы текущей категории."""
    i =  models.Item.objects.filter(category=category)
    if producer:
        i = i.filter(producer=producer)
    return i

def get_sub_cats_items(category):
    """Функция возвращает элементы всех дочерних категорий,
    включая указанную."""
    cats = set(get_sub_cats(category))
    return models.Item.objects.filter(category__in=cats)

def get_currcat_procs(category):
    """Функция возвращает производителей текущей категории."""
    return set([l.producer for l in get_currcat_items(category)])
    
def get_sub_cats_procs(category):
    """
    Возвращает производителей текущей и дочерних категорий.
    """
    return set([l.producer for l in get_sub_cats_items(category) | get_currcat_items(category)])
