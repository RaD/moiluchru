# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from cargo.shop.models import Category, Producer, Item

def main_page(request):
    """This function shows the main page of a site."""
    
def subcats(request, category):
    """ Функция для отображения подчинённых категорий. """
    current_category = Category.objects.get(id=category)
    return render_to_response('shop-subcats.html',
                              {'parent_cats': get_parent_cats(current_category),
                               'categories': current_category.category_set.all(),
                               'producers': get_currcat_procs(current_category),
                               'items': get_currcat_items(category)
                               })

def showitem(request, item):
    curr_item = Item.objects.get(id=item)
    return render_to_response('shop-item.html',
                              {'item': curr_item,
                               'parent_cats': get_parent_cats(curr_item.category),
                               })
    

def get_parent_cats(category):
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
