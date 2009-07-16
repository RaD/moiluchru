# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils.translation import gettext_lazy as _

from tagging.models import Tag
from tagging.utils import calculate_cloud

from shop import common
from shop import models
from shop.forms import DivErrorList, SearchForm, OfferForm
from shop.classes import CartItem

from snippets import render_to, columns, paginate_by

sort = ['', '-buys', 'buys', '-sort_price', 'sort_price']

### Контекст
def cart_ctx_proc(request):
    """ Контекстный процессор для заполнения данных о корзине и для
    вывода поисковой формы на каждой странице. """
    session = request.session
    form = SearchForm(auto_id='field_%s',
                      initial={'userinput': session.get('searchquery', ''),
                               'howmuch': session.get('howmuch_id', 1)})
    menu = [(1, u'/', _(u'Main')), (2, u'/search/', _(u'Search')), (3, u'/items/', _(u'Items')),
            (4, u'/text/shipping/', _(u'Shipping')), (5, u'/text/map/', _(u'Map'))]
    cloud = calculate_cloud(Tag.objects.usage_for_model(models.Item, counts=True))
    cp = {'min_pct': 75, 'max_pct': 150, 'steps': 4}
    step_pct = int((cp['max_pct'] - cp['min_pct'])/(cp['steps'] - 1))
    for i in cloud:
        i.font_size = (i.font_size - 1) * step_pct + cp['min_pct']
    return {'debug': getattr(settings, 'DEBUG', False),
            'jabber': getattr(settings, 'JABBER_ENGINE', False),
            'site_title': getattr(settings, 'SITE_TITLE', 'Установите название сайта'),
            'site_subtitle': getattr(settings, 'SITE_SUBTITLE', 'Установите текст'),
            'google_analytics': getattr(settings, 'GOOGLE_ANALYTICS', False),
            'menu': menu, 'path': request.path,
            'form': form,
            'tags': cloud,
            'top_cats': common.top_categories(),
            'cart_count': session.get('cart_count', 0),
            'cart_price': session.get('cart_price', 0.00)}

### Страница с поисковым запросом
@render_to('shop/search.html', cart_ctx_proc)
def search_query(request):
    from shop.forms import get_search_form # воспользуемся фабрикой поисковых форм
    context = {
        'searchform': SearchForm(), 
        'mainsearchform': get_search_form('MainSearchForm', initial={'is_present': True}),
        'sizesearchform': get_search_form('SizeSearchForm'),
        'fullsearchform': get_search_form('FullSearchForm'),
        'page_title': u'Мой Луч'
        }

    # здесь мы обрабатываем ситуацию вызова поисковых форм после
    # обнаружения ошибки в поисковом запросе
    try:
        (form_name, post, desc) = request.session['error']
        del(request.session['error'])
        context.update({'error_desc': desc})
        if form_name == 'simple':
            context.update({'searchform': SearchForm(post)})
        else:
            context.update({ form_name.lower():  get_search_form(form_name, data=post) })
    except KeyError:
        pass

    return context

### Страница с результатами поиска
@render_to('shop/result.html', cart_ctx_proc)
@columns('items', 1)
@paginate_by('items', 'page', getattr(settings, 'SHOP_ITEMS_PER_PAGE', 20))
def search_results(request):
    """ Функция для результатов поиска по магазину. """
    common.does_cart_exist(request)
    sort_type = request.session.get('sort_type', 1)
    context = {'page_title': u'Результаты поискового запроса',
               'url': '/result/', 'sort_type': sort_type}

    if request.method == 'POST':
        full_search = 'simple' in request.POST and request.POST['simple'] == 'False'

        form = SearchForm(request.POST)
        if form.is_valid():
            clean = form.cleaned_data
            # поиск по тексту
            if clean['userinput'] == u'':
                items = models.Item.objects.all()
            else:
                items = models.Item.objects.filter(Q(title__search=u'*"%s"*' % clean['userinput']) |
                                                   Q(desc__search=u'*"%s"*' % clean['userinput']) |
                                                   Q(tags__search=u'*"%s"*' % clean['userinput']))
            # поиск по дополнительным параметрам товара
            if full_search:
                from shop.forms import get_search_form # воспользуемся фабрикой поисковых форм

                for key in ['MainSearchForm', 'SizeSearchForm', 'FullSearchForm']:
                    form = get_search_form(key, data=request.POST)
                    if form.is_valid():
                        subset = form.search()
                        # для inline моделей фильтр создаётся немного по другому, т.к. у них item.id
                        if key == 'MainSearchForm':
                            id_array = [i.id for i in subset]
                        else:
                            id_array = [i.item.id for i in subset]
                        items = items.filter(id__in=id_array)
                    else:
                        try: # сохраняем имя класса формы
                            request.session['error'] = (key, request.POST, 
                                                        u'Ошибка во введённых данных. Проверьте их правильность.')
                        except KeyError:
                            raise Http404
                        return HttpResponseRedirect('/search/')

            request.session['searchquery'] = clean['userinput']
            request.session['howmuch_id'] = clean['howmuch']
            request.session['cached_items'] = items # кэшируем для paginator
        else:
            request.session['error'] = ('simple', request.POST, 
                                        u'Ошибка во введённых данных. Проверьте их правильность.')
            return HttpResponseRedirect('/search/')
    
        context.update(
            {'items': items.order_by(sort[sort_type]),
             'search_query': clean['userinput']})
    else: # обращение через paginator
        try:
            items = request.session.get('cached_items').order_by(sort[sort_type])
        except:
            # видать прошли по ссылке напрямую, отправим на страницу поиска
            return HttpResponseRedirect('/search/')
        context.update(
            {'items': items,
             'search_query': request.session.get('searchquery', '')})
    return context

### Страница с результатами поиска по тегу
def tag_results(request, tag):
    """ Функция для результатов поиска по тегу. """
    items = models.Item.objects.filter(Q(tags__search='%s' % tag))
    request.session['searchquery'] = tag
    request.session['cached_items'] = items # кэшируем для paginator
    return HttpResponseRedirect(u'/result/')

### Главная страница
@render_to('shop/main.html', cart_ctx_proc)
def show_main_page(request):
    """ Функция для отображения главной страницы сайта.  Осуществляем
    проверку поддержки Cookie. """
    if request.session.test_cookie_worked():
        common.does_cart_exist(request)
    else:
        request.session.set_test_cookie()

    try:
        items = models.Item.objects.order_by('-buys')[:getattr(settings, 'ITEMS_ON_MAIN_PAGE', 10)]
    except models.Item.DoesNotExist:
        items = 0

    return {
        'page_title': u'Мой Луч',
        'menu_current': 1,
        'items_col1': items[:getattr(settings, 'ITEMS_ON_MAIN_PAGE', 10)/2],
        'items_col2': items[getattr(settings, 'ITEMS_ON_MAIN_PAGE', 10)/2:]}

### Страница со списком товаров
@render_to('shop/itemlist.html', cart_ctx_proc)
@columns('items', 2)
@paginate_by('items', 'page', getattr(settings, 'SHOP_ITEMS_PER_PAGE', 20))
def show_items(request):
    """ Отображение списка товаров. """
    sort_type = request.session.get('sort_type', 1)

    common.does_cart_exist(request)

    # получаем отсортированные товары всех категорий
    items = common.category_items().order_by(sort[sort_type]) 
    request.session['cached_items'] = items # кэшируем для paginator
    
    return {
        'page_title': u'Товары',
        'menu_current': 3, 'title': _(u'Items'),
        'categories': models.Category.objects.all(),
        'sort_type': sort_type, 
        'url': reverse(show_items), # для многостраничности
        'items': items}

### Страница со списком товаров указанной категории
@render_to('shop/itemlist.html', cart_ctx_proc)
@columns('items', 2)
@paginate_by('items', 'page', getattr(settings, 'SHOP_ITEMS_PER_PAGE', 20))
def show_category_page(request, category_id=None):
    """ Функция для отображения подчинённых категорий. """
    sort_type = request.session.get('sort_type', 1)

    common.does_cart_exist(request)

    items = common.category_items(category_id).order_by(sort[sort_type])
    request.session['cached_items'] = items # кэшируем для paginator
    try:
        c = models.Category.objects.get(id=category_id)
    except models.Category.DoesNotExist:
        return HttpResponseRedirect(u'/items/')

    return {
        'page_title': u'Категория товаров',
        'menu_current': 3, 'title': _(u'Items of the category'),
        'categories': models.Category.objects.all(),
        'category_id': int(category_id),
        'url': c.get_absolute_url(), # для многостраничности
        'sort_type': sort_type, 
        'items': items}

### Страница со списком товаров указанной категории
@render_to('shop/itemlist.html', cart_ctx_proc)
@columns('items', 2)
@paginate_by('items', 'page', getattr(settings, 'SHOP_ITEMS_PER_PAGE', 20))
def show_category_page_by_title(request, category_title=None):
    """ Функция для отображения подчинённых категорий. """
    sort_type = request.session.get('sort_type', 1)

    common.does_cart_exist(request)

    try:
        category = models.Category.objects.get(title=category_title)
        items = models.Item.objects.filter(category=category).order_by(sort[sort_type])
        request.session['cached_items'] = items # кэшируем для paginator
    except models.Category.DoesNotExist:
        raise Http404

    return {
        'page_title': u'Категория товаров',
        'menu_current': 3, 'title': _(u'Items of the category'),
        'categories': models.Category.objects.all(),
        'category_id': category.id,
        'url': category.get_absolute_url(), # для многостраничности
        'sort_type': sort_type, 
        'items': items}

### Страница со списком товаров указанной коллекции
@render_to('shop/itemlist.html', cart_ctx_proc)
@columns('items', 2)
@paginate_by('items', 'page', getattr(settings, 'SHOP_ITEMS_PER_PAGE', 20))
def show_collection_page(request, collection_id=None):
    """ Функция для отображения подчинённых категорий. """
    sort_type = request.session.get('sort_type', 1)

    common.does_cart_exist(request)

    try:
        collection = models.Collection.objects.get(id=collection_id)
        items = models.Item.objects.filter(collection=collection_id).order_by(sort[sort_type])
        request.session['cached_items'] = items # кэшируем для paginator
        categories_of_collection = set([i.category for i in items])
    except models.Item.DoesNotExist:
        # FIXME
        return HttpResponseRedirect(u'/items/')
    except models.Collection.DoesNotExist:
        raise Http404

    return {
        'page_title': u'Коллекция товаров',
        'menu_current': 3, 'title': _(u'Items of the collection'),
        'child_cats': categories_of_collection,
        'collection_id': collection_id,
        'url': collection.get_absolute_url(), # для многостраничности
        'sort_type': sort_type, 
        'items': items}

### Страница с описанием товара
@render_to('shop/item.html', cart_ctx_proc)
def show_item_page(request, item_id):
    """ Отображение подробной информации о товаре. """
    common.does_cart_exist(request)
    try:
        item = models.Item.objects.get(id=item_id)
        collection = models.Item.objects.filter(collection=item.collection, 
                                                collection__isnull=False).exclude(id=item.id)
        return {
            'page_title': item.title,
            'menu_current': 3,
            'item': item, 'collection': collection,
            'lamp': item.get_lamp(), 'addons': item.get_size(),
            'parent_cats': common.parent_categories(item.category.id)}
    except models.Item.DoesNotExist:
        raise Http404
    
### Страница с описанием товара
@render_to('shop/item.html', cart_ctx_proc)
def show_item_by_title_page(request, item_title):
    """ Отображение подробной информации о товаре. """
    common.does_cart_exist(request)
    try:
        item = models.Item.objects.get(title=item_title)
        collection = models.Item.objects.filter(collection=item.collection, collection__isnull=False).exclude(id=item.id)
        return {
            'page_title': item.title,
            'menu_current': 3,
            'item': item, 'collection': collection,
            'lamp': item.get_lamp(), 'addons': item.get_size(),
            'parent_cats': common.parent_categories(item.category.id)}
    except models.Item.DoesNotExist:
        raise Http404
    
# Страница с содержимым корзины
@render_to('shop/cart.html', cart_ctx_proc)
def show_cart(request):
    """ Отображение содержимого корзины. """
    items = []
    cart = request.session.get('cart_items', {})
    if len(cart) == 0:
        items = None
    else:
        for i in cart:
            record = models.Item.objects.get(id=i)
            items.append(CartItem(record, cart[i]['count'], cart[i]['price']))
    return {
        'page_title': u'Корзина',
        'cart': cart, # для отключения кнопок
        'cart_items': items,
        'cart_show' : 'yes',
        'categories': models.Category.objects.filter(parent__isnull=True)}

#
@render_to('shop/offer.html', cart_ctx_proc)
def show_offer(request):
    """ Отображение формы для ввода данных о покупателе.  Обработка
    пользовательского ввода. """
    if not 'cart_items' in request.session or request.session['cart_count'] == 0:
        return HttpResponseRedirect('/')

    if request.method == 'POST':
        form = OfferForm(request.POST)
        if form.is_valid():
            # обработать форму
            try:
                clean = form.cleaned_data
                phone_type = clean['phonetype']
                buyer, created = models.Buyer.objects.get_or_create(
                    lastname = clean['fname'], firstname = clean['iname'], secondname = clean['oname'],
                    address = clean['address'], email =  clean['email']
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
                    item.buys += 1
                    item.save()
                    # учтём статистику
                    producer = item.producer
                    producer.buys += 1
                    producer.save()
                return HttpResponseRedirect('/ordered/')
            except Exception, e:
                return HttpResponse('bad form data: %s' % e)  #FIXME: DECORATOR
        else:
            form = OfferForm(request.POST, auto_id='field_%s', error_class=DivErrorList)
            return {'form_offer': form, 'cart_show' : 'yes'}
    else:
        form = OfferForm(auto_id='field_%s')
        return {
            'page_title': u'Оформление заказа',
            'form_offer': form, 'cart_show' : 'yes'}
    
# Заказ выполнен, отсылаем уведомление, очищаем корзину.
@render_to('shop/ordered.html', cart_ctx_proc)
def show_ordered(request):
    common.init_cart(request)
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
    return {'page_title': u'Мой Луч'}
    
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
        return HttpResponseRedirect('/%s/' % mode) #FIXME

# Страница с текстом
@render_to('shop/text.html', cart_ctx_proc)
def show_text_page(request, label):
    """ Отображение страницы с текстом. """
    modes = {'shipping': 4, 'contact': 5}
    from text.views import text
    return {            
        'page_title': u'Мой Луч',
        'menu_current': modes.get(label, 0),
        'text': text(request, label)}

@render_to('404.html', cart_ctx_proc)
def handler404(request):
    if request.session.test_cookie_worked():
        common.does_cart_exist(request)
    else:
        request.session.set_test_cookie()

    try:
        items = models.Item.objects.order_by('-buys')[:getattr(settings, 'ITEMS_ON_MAIN_PAGE', 10)]
    except models.Item.DoesNotExist:
        items = 0
    return {'menu_current': 1, 'page_title': '404: Страница не найдена...',
            'items_col1': items[:getattr(settings, 'ITEMS_ON_MAIN_PAGE', 10)/2],
            'items_col2': items[getattr(settings, 'ITEMS_ON_MAIN_PAGE', 10)/2:]}

@render_to('500.html', cart_ctx_proc)
def handler500(request):
    if request.session.test_cookie_worked():
        common.does_cart_exist(request)
    else:
        request.session.set_test_cookie()

    try:
        items = models.Item.objects.order_by('-buys')[:getattr(settings, 'ITEMS_ON_MAIN_PAGE', 10)]
    except models.Item.DoesNotExist:
        items = 0
    return {'menu_current': 1, 'page_title': '500: Что-то с моим кодом...',
            'items_col1': items[:getattr(settings, 'ITEMS_ON_MAIN_PAGE', 10)/2],
            'items_col2': items[getattr(settings, 'ITEMS_ON_MAIN_PAGE', 10)/2:]}
