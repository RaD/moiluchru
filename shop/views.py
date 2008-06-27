# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.utils.translation import ugettext, gettext_lazy as _
from django.core import validators
from cargo.shop.models import Category, Producer, Item

def show_main_page(request):
    """
    Функция для отображения главной страницы сайта.
    Осуществляем проверку поддержки Cookie.
    """
    request.session.set_test_cookie()
    return render_to_response('shop-show-main.html',
                              {'queryset': Category.objects.filter(parent__isnull=True)[:5]})
    
def show_category_page(request, category):
    """
    Функция для отображения подчинённых категорий.
    """
    if request.session.test_cookie_worked():
        request.session["basket"] = "test"
    else:
        raise validators.ValidationError("Your Web browser doesn't appear " +
                                         "to have cookies enabled. " +
                                         "Cookies are required for logging in.")
    c = Category.objects.get(id=category)
    return render_to_response('shop-show-category.html',
                              {'parent_cats': get_parent_cats(c),
                               'categories': c.category_set.all(),
                               'producers': get_currcat_procs(c),
                               'items': get_currcat_items(category)
                               })

def show_item_page(request, item):
    curr_item = Item.objects.get(id=item)
    return render_to_response('shop-show-item.html',
                              {'item': curr_item,
                               'parent_cats': get_parent_cats(curr_item.category),
                               })
    

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
