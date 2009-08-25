# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.utils.translation import gettext_lazy as _

from shop import views as v_shop
from shop import forms as f_shop

from snippets import render_to, columns, paginate_by

sort_variants = ['', '-buys', 'buys', '-sort_price', 'sort_price']

def common_context(request):
    if not 'cart_items' in request.session:
        init_cart(request)
    context = {
        'category_list': v_shop.get_all_categories(),
        'tag_list': v_shop.get_all_tags(),
        'debug': getattr(settings, 'DEBUG', False),
        'jabber': getattr(settings, 'JABBER_ENGINE', False),
        'search_query': request.session.get('searchquery', 'Поиск: Введите запрос и нажмите [Enter]'),
        'sort_type': request.session.get('sort_type', 1),
        'cart_count': request.session.get('cart_count', 0),
        'cart_price': request.session.get('cart_price', 0.00),
        }
    return context

### Поиск по тегу
def tag_search(request, tag):
    items = v_shop.tag_search(request, tag)
    return HttpResponseRedirect(u'/result/')

### Выдача расширенного поискового интерфейса
@render_to('search.html', common_context)
def search_query(request):
    return {}

### Выдача результатов поискового запроса
@render_to('list.html', common_context)
@columns('items', 2)
@paginate_by('items')
def search_results(request):
    items = v_shop.get_search_results(request)
    if items is None:
        return HttpResponseRedirect('/search/')
    return {
        'page_title': '%s : %s : %s' % (_(u'Search'), _(u'Results'), settings.SITE_TITLE,),
        'mode': 'list', 'cat_mode': 'search',
        'items': items.order_by(sort_variants[request.session.get('sort_type', 1)]),
        'url': '/result/',
        'search_query': request.session.get('searchquery', ''),
        }

### Страница со списком товаров указанной категории
@render_to('list.html', common_context)
@columns('items', 2)
@paginate_by('items')
def category(request, title=None):
    if 'search_query' in request.session:
        del(request.session['search_query'])
    (category, items) = v_shop.get_items_by_category(request, title)
    return {
        'page_title': '%s : %s : %s' % (_(u'Category'), category, settings.SITE_TITLE),
        'mode': 'list',
        'this': category,
        'items': items,
        'url': '/category/%s/' % (title,),
        }

### Страница со списком товаров указанной коллекции
@render_to('list.html', common_context)
@columns('items', 2)
@paginate_by('items')
def collection(request, id=None):
    if 'search_query' in request.session:
        del(request.session['search_query'])
    (collection, items) = v_shop.get_items_by_collection(request, id)
    return {
        'page_title': '%s : %s' % (_(u'Collection'), settings.SITE_TITLE, ),
        'mode': 'list',
        'this': collection,
        'items': items,
        'url': '/collection/%s/' % (id,),
        }

### Страница с описанием товара
@render_to('item.html', common_context)
def item(request, id=None):
    if 'search_query' in request.session:
        del(request.session['searchquery'])
    (item, collection, previous, next) = v_shop.get_item_info(request, id)

    return {
        'page_title': '%s : %s : %s' % (_(u'Item'), item, settings.SITE_TITLE),
        'mode': 'item',
        'this': item.category,
        'item': item, 'collection': collection,
        'previous': previous, 'next': next,
        'lamp': item.get_lamp(), 'addons': item.get_size(),
        }

### Отображение содержимого корзины.
@render_to('cart.html', common_context)
def show_cart(request):
    return {
        'page_title': '%s : %s' % (_(u'Cart'), settings.SITE_TITLE, ),
        'mode': 'cart',
        'items': v_shop.get_cart_items(request),
        }

### Отображение формы заказа.
@render_to('order.html', common_context)
def show_order(request):
    error_desc = None
    form = f_shop.OfferForm(request.POST or None,
                            cart = request.session.get('cart_items', {}),
                            count = request.session.get('cart_count', 0),
                            total = request.session.get('cart_price', 0.00)
                            )
    if request.method == 'POST' and form.is_valid():
        try:
            form.save()
            return HttpResponseRedirect('/profit/')
        except Exception, e:
            error_desc = e
    return {
        'page_title': '%s : %s' % (_(u'Order'), settings.SITE_TITLE, ),
        'form': form,
        'error_desc': error_desc,
        }

### Скажем спасибо за заказ
@render_to('profit.html', common_context)
def show_profit(request):
    v_shop.init_cart(request)
    if getattr(settings, 'JABBER_NOTIFICATION', False) and not getattr(settings, 'DEBUG', False):
        import xmpp, time
        jid = xmpp.protocol.JID(getattr(settings, 'JABBER_ID', None))
        cl = xmpp.Client(jid.getDomain(), debug=[])
        conn = cl.connect()
        if conn:
            auth = cl.auth(jid.getNode(), 
                           getattr(settings, 'JABBER_PASSWORD', None),
                           resource=jid.getResource())
            if auth:
                for recipient in getattr(settings, 'JABBER_RECIPIENTS', None):
                    id = cl.send(xmpp.protocol.Message(recipient, 'Внимание! Есть заказ!'))
                    # Некоторые старые сервера не отправляют сообщения,
                    # если вы немедленно отсоединяетесь после отправки
                    time.sleep(1)
    return {
        'page_title': '%s : %s' % (_(u'Order processed'), settings.SITE_TITLE, ),
        }

# Метод для изменения параметров сортировки
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
        raise Http404
