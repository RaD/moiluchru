# -*- coding: utf-8 -*-
from django.db.models.query import QuerySet
#from django.core import validators
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
	pass
#        raise validators.ValidationError("Your Web browser doesn't appear " +
#                                         "to have cookies enabled. " +
#                                         "Cookies are required for logging in.")

def top_categories():
    return list(models.Category.objects.filter(parent__isnull=True))

def parent_categories(category_id):
    if int(category_id) == 0:
        return [];
    else:
        category = models.Category.objects.get(id=category_id)
        a = [category]
        while True:
            if category.parent:
                a.insert(0, category.parent)
                category = category.parent
            else:
                break
        return a

def subcategories(category_id=0):
    """Функция возвращает все дочерние категории,
    даже дочерние дочерних и так далее."""
    if int(category_id) == 0:
        return child_categories()
    else:
        category = models.Category.objects.get(id=category_id)
        result = list(category.category_set.all())
        return reduce(lambda a,b: a + b,
                      [subcategories(l.id) for l in result],
                      result)

def child_categories(category_id=0):
    """ Функция возвращает дочерние категории для указанной."""
    if int(category_id) == 0:
        return top_categories()
    else:
        category = models.Category.objects.get(id=category_id)
        return list(category.category_set.all())
        
def category_items(category_id, producer_id=None):
    """Функция возвращает элементы текущей категории."""
    if int(category_id) == 0:
        i = models.Item.objects.all() 
    else:
        i = models.Item.objects.filter(category=category_id)

    # отображать товары из подкатегорий только в том случае,
    # если нет товаров в текущей категории
    if not i:
        i |= subcategories_items(category_id)

    if producer_id:
        i = i.filter(producer=producer_id)
    return i

def subcategories_items(category_id):
    """Функция возвращает элементы всех дочерних категорий,
    включая указанную."""
    cats = set(subcategories(category_id))
    return models.Item.objects.filter(category__in=cats)

def category_producers(category_id):
    """ Возвращает производителей текущей и дочерних категорий. """
    return set([l.producer for l in category_items(category_id)])
    
