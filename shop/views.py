# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import gettext_lazy as _

from moiluchru.shop import common
from moiluchru.shop.models import Item, Category, Producer, Buyer, Phone, Order, \
    OrderStatus, OrderDetail, Lamp
from moiluchru.shop.forms import DivErrorList, SearchForm, OfferForm
from moiluchru.shop.classes import CartItem

from moiluchru.snippets import render_to, columns, paginate_by

def cart_ctx_proc(request):
    """ Контекстный процессор для заполнения данных о корзине и для
    вывода поисковой формы на каждой странице. """
    session = request.session
    form = SearchForm(auto_id='field_%s',
                      initial={'userinput': session.get('searchquery', ''),
                               'howmuch': session.get('howmuch_id', 1)})
    menu = [(1, u'/', _(u'Main')), (2, u'/news/', _(u'News')), (3, u'/items/', _(u'Items')),
            (4, u'/text/shipping/', _(u'Shipping')), (5, u'/text/contact/', _(u'Contact'))]
    return {'debug': settings.DEBUG,
            'site_title': settings.SITE_TITLE,
            'site_subtitle': settings.SITE_SUBTITLE,
            'google_analytics': settings.GOOGLE_ANALYTICS,
            'menu': menu, 'path': request.path,
            'form': form,
            'top_cats': common.top_categories(),
            'cart_count': session.get('cart_count', 0),
            'cart_price': session.get('cart_price', 0.00)}

@render_to('shop/main.html', cart_ctx_proc)
def show_main_page(request):
    """ Функция для отображения главной страницы сайта.  Осуществляем
    проверку поддержки Cookie. """
    if request.session.test_cookie_worked():
        common.does_cart_exist(request)
    else:
        request.session.set_test_cookie()

    try:
        items = Item.objects.order_by('-buys')[:settings.ITEMS_ON_MAIN_PAGE]
    except Item.DoesNotExist:
        items = 0
    return {'menu_current': 1,
            'items_col1': items[:settings.ITEMS_ON_MAIN_PAGE/2],
            'items_col2': items[settings.ITEMS_ON_MAIN_PAGE/2:]}

@render_to('shop/search.html', cart_ctx_proc)
@columns('items', 1)
@paginate_by('items', 'page', settings.SHOP_ITEMS_PER_PAGE)
def search_results(request):
    """ Функция для результатов поиска по магазину. """
    common.does_cart_exist(request)
    sort_type = request.session.get('sort_type', 1)
    sort = ['', '-buys', 'buys', '-price', 'price']
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            clean = form.cleaned_data
            items = Item.objects.filter(Q(title__search='*%s*' % clean['userinput']) |
                                        Q(desc__search='*%s*' % clean['userinput']) |
                                        Q(tags__search='*%s*' % clean['userinput'])
                                        ).order_by(sort[sort_type])
            z = [settings.SHOP_ITEMS_PER_PAGE, 10, 25, 50];
            request.session['searchquery'] = clean['userinput']
            request.session['howmuch_id'] = clean['howmuch']
            return {'items': items,
                    'search_query': clean['userinput'],
                    'url': '/shop/search/',
                    'sort_type': sort_type}
        else:
            return HttpResponseRedirect('/shop/')
    else:
        userinput = request.session.get('searchquery', '')
        item_per_page = request.session.get('item_per_page', settings.SHOP_ITEMS_PER_PAGE)
        i = Item.objects.filter(Q(title__search=userinput) |
                                       Q(desc__search=userinput))
        p = Paginator(i.order_by(sort[sort_type]), item_per_page)
        return {'menu_current': 3,
                'items': p.page(page).object_list,
                'search_query': userinput,
                'url': '/shop/search/',
                'sort_type': sort_type, 
                'page': p.page(page), 'page_range': p.page_range}

@render_to('shop/category.html', cart_ctx_proc)
@columns('items', 2)
@paginate_by('items', 'page', settings.SHOP_ITEMS_PER_PAGE)
def show_items(request):
    """ Представление для отображения общей страницы с новинками. """
    sort = ['', '-buys', 'buys', '-sort_price', 'sort_price']
    sort_type = request.session.get('sort_type', 1)

    common.does_cart_exist(request)

    # получаем отсортированные товары всех категорий
    items = common.category_items().order_by(sort[sort_type]) 
    
    return {'menu_current': 3,
            'child_cats': common.child_categories(),
            'sort_type': sort_type, 
            'url': reverse(show_items), # для многостраничности
            'items': items}

@render_to('shop/category.html', cart_ctx_proc)
@columns('items', 2)
@paginate_by('items', 'page', settings.SHOP_ITEMS_PER_PAGE)
def show_category_page(request, category_id=None):
    """ Функция для отображения подчинённых категорий. """
    sort = ['', '-buys', 'buys', '-price', 'price']
    sort_type = request.session.get('sort_type', 1)

    common.does_cart_exist(request)

    items = common.category_items(category_id).order_by(sort[sort_type])
    try:
        c = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        return HttpResponseRedirect(u'/items/')

    return {'menu_current': 3,
            'parent_cats': common.parent_categories(category_id),
            'child_cats': common.child_categories(category_id),
            'category_id': category_id,
            'url': c.get_absolute_url(), # для многостраничности
            'sort_type': sort_type, 
            'items': items}

@render_to('shop/category.html', cart_ctx_proc)
def show_producer_page(request, producer_id, page, category_id=0):
    """ Функция для отображения товаром для указанного производителя
    из всех подчинённых категорий. """
    common.does_cart_exist(request)
    p = Producer.objects.get(id=producer_id)
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

@render_to('shop/item.html', cart_ctx_proc)
def show_item_page(request, item_id):
    """ Отображение информации о товаре. """
    common.does_cart_exist(request)
    try:
        item = Item.objects.get(id=item_id)
        return {'menu_current': 3,
                'item': item, 'lamp': item.get_lamp(), 'addons': item.get_size(),
                'parent_cats': common.parent_categories(item.category.id)}
    except Item.DoesNotExist:
        pass # FIXME
    
@render_to('shop/cart.html', cart_ctx_proc)
def show_cart(request):
    """ Отображение содержимого корзины. """
    items = []
    cart = request.session.get('cart_items', {})
    if len(cart) == 0:
        items.append(CartItem("Нет товаров", 0, 0.00))
    else:
        for i in cart:
            record = Item.objects.get(id=i)
            items.append(CartItem(record.title, cart[i]['count'], cart[i]['price']))
    return {'cart': cart, # для отключения кнопок
            'cart_items': items,
            'cart_show' : 'yes',
            'categories': Category.objects.filter(parent__isnull=True)}

@render_to('shop/offer.html', cart_ctx_proc)
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
                buyer, created = Buyer.objects.get_or_create(
                    lastname = clean['fname'], firstname = clean['iname'], secondname = clean['oname'],
                    address = clean['address'], email =  clean['email']
                    )
                phone, created = Phone.objects.get_or_create(
                    number = clean['phone'], type = phone_type, owner = buyer
                    )
                order, created = Order.objects.get_or_create(
                    buyer = buyer,
                    count = request.session.get('cart_count', 0),
                    totalprice = request.session.get('cart_price', 0.00),
                    comment = clean['comment'],
                    status = OrderStatus.objects.get(id=1)
                    )
                cart = request.session.get('cart_items', {})
                for i in cart:
                    item = Item.objects.get(id=i)
                    orderdetail = OrderDetail(order = order, item = item,
                                                     count = cart[i]['count'],
                                                     price = cart[i]['price'])
                    orderdetail.save()
                    # убираем товар с витрины
                    item.buys += 1
                    item.save()
                    # учтём статистику
                    producer = item.producer
                    producer.buys += 1
                    producer.save()
                return HttpResponseRedirect('/shop/ordered/')
            except Exception, e:
                return HttpResponse('bad form data: %s' % e)  #FIXME: DECORATOR
        else:
            form = OfferForm(request.POST, auto_id='field_%s', error_class=DivErrorList)
            return {'form_offer': form, 'cart_show' : 'yes'}
    else:
        form = OfferForm(auto_id='field_%s')
        return {'form_offer': form, 'cart_show' : 'yes'}

@render_to('shop/ordered.html', cart_ctx_proc)
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

@render_to('shop/text.html', cart_ctx_proc)
def show_text_page(request, label):
    """ Отображение страницы с текстом. """
    modes = {'shipping': 4, 'contact': 5}
    from moiluchru.text.views import text
    return {'menu_current': modes.get(label, 0),
            'text': text(request, label)}
