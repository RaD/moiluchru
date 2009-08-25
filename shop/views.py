# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils.translation import gettext_lazy as _

from tagging.models import Tag
from tagging.utils import calculate_cloud

from shop import models
from shop.forms import DivErrorList, SearchForm, OfferForm

from snippets import render_to, columns, paginate_by

def get_all_categories():
    return models.Category.objects.all()

def get_all_tags():
    cloud = calculate_cloud(Tag.objects.usage_for_model(models.Item, counts=True))
    cp = {'min_pct': 75, 'max_pct': 150, 'steps': 4}
    step_pct = int((cp['max_pct'] - cp['min_pct'])/(cp['steps'] - 1))
    for i in cloud:
        i.font_size = (i.font_size - 1) * step_pct + cp['min_pct']
    return cloud

def get_items_by_category(request, title):
    class Category:
        def __init__(self, title, slug):
            self.title = title
            self.slug = slug
        def __unicode__(self):
            return self.title

    try:
        if title == 'popular':
            category = Category(u'Популярные', u'popular')
            items = models.Item.objects.all().order_by('-buys')
        elif title == 'new':
            category = Category(u'Новинки', u'new')
            items = models.Item.objects.all().order_by('-reg_date')
        else:
            category = models.Category.objects.get(slug=title)
            items = models.Item.objects.filter(category=category) #.order_by(sort[sort_type])
        # not used: request.session['cached_items'] = items # кэшируем для paginator
    except models.Item.DoesNotExist:
        raise Http404
    request.session['cached_items'] = items
    return (category, items)

def get_items_by_collection(request, id):
    try:
        collection = models.Collection.objects.get(id=id)
        items = models.Item.objects.filter(collection=id)
        request.session['cached_items'] = items # кэшируем для paginator
    except models.Collection.DoesNotExist:
        raise Http404
    return (collection, items)
    
def get_item_info(request, id):
    try:
        item = models.Item.objects.get(id=id)
        collection = models.Item.objects.filter(collection=item.collection, 
                                                collection__isnull=False).exclude(id=item.id)
        cached_items = request.session.get('cached_items', [])
        index = list(cached_items).index(filter(lambda x: x.id==item.id, cached_items)[0])
        previous = next = None
        if index > 0:
            previous = cached_items[index - 1]
        if index < len(cached_items) - 1:
            next = cached_items[index + 1]
        return (item, collection, previous, next)
    except models.Item.DoesNotExist:
        raise Http404

def init_cart(request):
    """ Инициализация корзины. """
    request.session['cart_items'] = {}
    request.session['cart_count'] = 0
    request.session['cart_price'] = 0.00

def tag_search(request, tag):
    """ Функция для результатов поиска по тегу. """
    items = models.Item.objects.filter(Q(tags__search='%s' % tag))
    request.session['searchquery'] = tag
    request.session['cached_items'] = items # кэшируем для paginator
    return items

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

def get_search_results(request):
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
                        return None

            request.session['searchquery'] = clean['userinput']
            request.session['howmuch_id'] = clean['howmuch']
            request.session['cached_items'] = items # кэшируем для paginator
        else:
            request.session['error'] = ('simple', request.POST, 
                                        u'Ошибка во введённых данных. Проверьте их правильность.')
            return None
    else: # обращение через paginator
        try:
            items = request.session.get('cached_items', [])
        except:
            # видать прошли по ссылке напрямую, отправим на страницу поиска
            return None
    return items

def get_cart_items(request):
    """ Возвращаем содержимое корзины. """

    class CartItem:
        """ Класс объекта-корзины. """
        def __init__(self, record, count, price):
            self.record = record
            self.count = count
            self.price = price
            self.cost = count * price

    cart = request.session.get('cart_items', {})
    if len(cart) == 0:
        items = None
    else:
        items = []
        for i in cart:
            record = models.Item.objects.get(id=i)
            items.append(CartItem(record, cart[i]['count'], cart[i]['price']))
    return items

def handler404(request):
    try:
        items = models.Item.objects.order_by('-buys')[:getattr(settings, 'ITEMS_ON_MAIN_PAGE', 10)]
    except models.Item.DoesNotExist:
        items = 0
    return {'menu_current': 1, 'page_title': '404: Страница не найдена...',
            'items_col1': items[:getattr(settings, 'ITEMS_ON_MAIN_PAGE', 10)/2],
            'items_col2': items[getattr(settings, 'ITEMS_ON_MAIN_PAGE', 10)/2:]}

def handler500(request):
    try:
        items = models.Item.objects.order_by('-buys')[:getattr(settings, 'ITEMS_ON_MAIN_PAGE', 10)]
    except models.Item.DoesNotExist:
        items = 0
    return {'menu_current': 1, 'page_title': '500: Что-то с моим кодом...',
            'items_col1': items[:getattr(settings, 'ITEMS_ON_MAIN_PAGE', 10)/2],
            'items_col2': items[getattr(settings, 'ITEMS_ON_MAIN_PAGE', 10)/2:]}
