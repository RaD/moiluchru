# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.utils.translation import ugettext, gettext_lazy as _
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.db.models import Q
from django.template import RequestContext
from django.core.paginator import Paginator

from cargo import settings
from cargo.shop import models, common
from cargo.shop.forms import DivErrorList, SearchForm, OfferForm
from cargo.shop.classes import CartItem

from cargo.snippets import render_to, paged

def cart_ctx_proc(request):
    """ Контекстный процессор для заполнения данных о корзине и для
    вывода поисковой формы на каждой странице. """
    session = request.session
    form = SearchForm(auto_id='field_%s',
                      initial={'userinput': session.get('searchquery', ''),
                               'howmuch': session.get('howmuch_id', 1)})
    return {'site_name': settings.SITE_NAME,
            'form': form,
            'howtos': models.Howto.objects.all(),
            'top_cats': common.top_categories(),
            'cart_count': session.get('cart_count', 0),
            'cart_price': session.get('cart_price', 0.00)}

@render_to('shop-main.html', cart_ctx_proc)
def show_main_page(request):
    """ Функция для отображения главной страницы сайта.  Осуществляем
    проверку поддержки Cookie. """
    if request.session.test_cookie_worked():
        common.does_cart_exist(request)
    else:
        request.session.set_test_cookie()
    return {'items': models.Item.objects.order_by('-buys')[:3],
            'producers': common.category_producers(0)}

@render_to('shop-howto.html', cart_ctx_proc)
def show_howto_page(request, howto):
    """ Функция для отображения вспомогательной информации. """
    common.does_cart_exist(request)
    return {'howto': models.Howto.objects.get(id=howto), 
            'back_to': request.META.get('HTTP_REFERER', '#')}

@render_to('shop-search.html', cart_ctx_proc)
@paged
def search_results(request, page):
    """ Функция для результатов поиска по магазину. """
    common.does_cart_exist(request)
    sort_type = request.session.get('sort_type', 1)
    sort = ['', '-buys', 'buys', '-price', 'price']
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            clean = form.cleaned_data
            i = models.Item.objects.filter(Q(title__search=clean['userinput']) |
                                           Q(desc__search=clean['userinput']))
            z = [settings.SHOP_ITEMS_PER_PAGE, 10, 25, 50];
            p = Paginator(i.order_by(sort[sort_type]), z[int(clean['howmuch'])-1])
            request.session['searchquery'] = clean['userinput']
            request.session['howmuch_id'] = clean['howmuch']
            return {'items': p.page(page).object_list,
                    'search_query': clean['userinput'],
                    'url': '/shop/search/',
                    'sort_type': sort_type, 
                    'page': p.page(page), 'page_range': p.page_range}
        else:
            return HttpResponseRedirect('/shop/')
    else:
        userinput = request.session.get('searchquery', '')
        item_per_page = request.session.get('item_per_page', settings.SHOP_ITEMS_PER_PAGE)
        i = models.Item.objects.filter(Q(title__search=userinput) |
                                       Q(desc__search=userinput))
        p = Paginator(i.order_by(sort[sort_type]), item_per_page)
        return {'items': p.page(page).object_list,
                'search_query': userinput,
                'url': '/shop/search/',
                'sort_type': sort_type, 
                'page': p.page(page), 'page_range': p.page_range}

@render_to('shop-category.html', cart_ctx_proc)
@paged
def show_category_page(request, category_id, page):
    """ Функция для отображения подчинённых категорий. """
    sort = ['', '-buys', 'buys', '-price', 'price']
    sort_type = request.session.get('sort_type', 1)
    common.does_cart_exist(request)
    i = common.category_items(category_id)
    c = models.Category.objects.get(id=category_id)
    p = Paginator(i.order_by(sort[sort_type]), settings.SHOP_ITEMS_PER_PAGE)
    return {'parent_cats': common.parent_categories(category_id),
            'child_cats': common.child_categories(category_id),
            'category_id': category_id,
            'producers': common.category_producers(category_id),
            'url': c.get_absolute_url(), # для многостраничности
            'sort_type': sort_type, 
            'items': p.page(page).object_list,
            'page': p.page(page), 'page_range': p.page_range}

@render_to('shop-category.html', cart_ctx_proc)
@paged
def show_producer_page(request, producer_id, page, category_id=0):
    """ Функция для отображения товаром для указанного производителя
    из всех подчинённых категорий. """
    common.does_cart_exist(request)
    p = models.Producer.objects.get(id=producer_id)
    i = common.category_items(category_id, producer_id)
    paginator = Paginator(i, settings.SHOP_ITEMS_PER_PAGE)
    return {'parent_cats': common.parent_categories(category_id),
            'child_cats': common.child_categories(category_id),
            'category_id': (category_id == 0) and None or category_id,
            #'currentproc': p,
            #'categories': child_cats,
            'producers': common.category_producers(category_id),
            'url': '/shop/producer/%s/%s/' % (producer_id, category_id),
            'items': paginator.page(page).object_list,
            'page': paginator.page(page), 'page_range': paginator.page_range}

@render_to('shop-item.html', cart_ctx_proc)
def show_item_page(request, item_id):
    """ Отображение информации о товаре. """
    common.does_cart_exist(request)
    i = models.Item.objects.get(id=item_id)
    return {'item': i,
            'item_remains': i.count - i.reserved,
            'js_onload': 'show_item_count_info(%s);' % item_id,
            'parent_cats': common.parent_categories(i.category.id)}
    
@render_to('shop-cart.html', cart_ctx_proc)
def show_cart(request):
    """ Отображение содержимого корзины. """
    items = []
    cart = request.session.get('cart_items', {})
    if len(cart) == 0:
        items.append(CartItem("Нет товаров", 0, 0.00))
    else:
        for i in cart:
            record = models.Item.objects.get(id=i)
            items.append(CartItem(record.title, cart[i]['count'], cart[i]['price']))
    return {'cart': cart, # для отключения кнопок
            'cart_items': items,
            'cart_show' : 'yes',
            'categories': models.Category.objects.filter(parent__isnull=True)}

@render_to('shop-offer.html', cart_ctx_proc)
def show_offer(request):
    """ Отображение формы для ввода данных о покупателе.  Обработка
    пользовательского ввода. """
    if not 'cart_items' in request.session or request.session['cart_count'] == 0:
        return HttpResponseRedirect('/shop/')

    if request.method == 'POST':
        form = OfferForm(request.POST)
        if form.is_valid():
            # обработать форму
            try:
                clean = form.cleaned_data
                phone_type = clean['phonetype']
                city = clean['city']
                buyer, created = models.Buyer.objects.get_or_create(
                    lastname = clean['fname'], firstname = clean['iname'], secondname = clean['oname'],
                    address = clean['address'], email =  clean['email'], city = city
                    )
                phone, created = models.Phone.objects.get_or_create(
                    number = clean['phone'], type = phone_type, owner = buyer
                    )
                order, created = models.Order.objects.get_or_create(
                    buyer = buyer,
                    count = request.session.get('cart_count', 0),
                    totalprice = request.session.get('cart_price', 0.00),
                    comment = clean['comment'],
                    status = models.OrderStatus.objects.get(id=1)
                    )
                cart = request.session.get('cart_items', {})
                for i in cart:
                    item = models.Item.objects.get(id=i)
                    orderdetail = models.OrderDetail(order = order, item = item,
                                                     count = cart[i]['count'],
                                                     price = cart[i]['price'])
                    orderdetail.save()
                    # убираем товар с витрины
                    item.count -= cart[i]['count']
                    item.reserved -= cart[i]['count']
                    item.buys += 1
                    item.save()
                    # учтём статистику
                    producer = item.producer
                    producer.buys += 1
                    producer.save()
                return HttpResponseRedirect('/shop/ordered/')
            except Exception, e:
                return HttpResponse('bad form data: %s' % e)
        else:
            form = OfferForm(request.POST, auto_id='field_%s', error_class=DivErrorList)
            return {'form_offer': form, 'cart_show' : 'yes'}
    else:
        form = OfferForm(auto_id='field_%s')
        return {'form_offer': form, 'cart_show' : 'yes'}

@render_to('shop-ordered.html', cart_ctx_proc)
def show_ordered(request):
    common.init_cart(request)
    return {}
    
def set_sort_mode(request, mode=1):
    if int(mode) in range(1,3):
        sort_type = int(request.session.get('sort_type', 1))
        if int(mode) == 1:
            if sort_type == 1:
                request.session['sort_type'] = 2
            else:
                request.session['sort_type'] = 1
        else:
            if sort_type == 3:
                request.session['sort_type'] = 4
            else:
                request.session['sort_type'] = 3
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '#'))
    else:
        return HttpResponseRedirect('/shop/%s/' % mode)
