# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.utils.translation import ugettext, gettext_lazy as _
from django.http import HttpResponse, HttpResponseRedirect
from django.core import validators
from django import newforms as forms
from cargo.shop import models

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
                              {'queryset': models.Category.objects.filter(parent__isnull=True)[:5],
                               'cart_count': request.session.get('cart_count', 0),
                               'cart_price': request.session.get('cart_price', 0.00)
                               })
    
def show_category_page(request, category):
    """
    Функция для отображения подчинённых категорий.
    """
    does_cart_exist(request)
    c = models.Category.objects.get(id=category)
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
    curr_item = models.Item.objects.get(id=item)
    return render_to_response('shop-show-item.html',
                              {'item': curr_item,
                               'item_remains' : curr_item.count - curr_item.reserved,
                               'parent_cats': get_parent_cats(curr_item.category),
                               'cart_count': request.session.get('cart_count', 0),
                               'cart_price': request.session.get('cart_price', 0.00)
                               })
    
def does_cart_exist(request):
    if request.session.test_cookie_worked():
        if not 'cart_items' in request.session:
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
        cnt = int(request.POST.get('item_count', 0))
        # проверить количество
        if id == 0 or cnt == 0:
            return HttpResponse('<result><code>302</code><desc>wrong parameters</desc></result>',
                                mimetype="text/xml")
        # инициализация корзины
        if not 'cart_items' in request.session:
            does_cart_exist(request)
        item = models.Item.objects.get(id=id)
        if int(item.count) < cnt:
            return HttpResponse('<result><code>301</code><desc>not enough items</desc>' +
                                '<cart_count>%s</cart_count><cart_price>%s</cart_price></result>'
                                % (request.session['cart_count'], request.session['cart_price']),
                                mimetype="text/xml")
        else:
            # зарезервировать товар
            item.reserved += cnt
            item.save()
            # добавить информацию о товаре в сессию
            price = item.price
            items = request.session.get('cart_items', {})
            if not id in items:
                items[id] = {}
            items[id]['count'] = int(items[id].get('count', 0)) + cnt
            items[id]['price'] = price
            # пересчитываем корзину
            request.session['cart_count'] = 0
            request.session['cart_price'] = 0.00
            for i in items:
                request.session['cart_count'] += int(items[i]['count'])
                request.session['cart_price'] += int(items[i]['count']) * float(models.Item.objects.get(id=i).price)
            # поместить в сессию
            request.session['cart_items'] = items
            return HttpResponse('<result><code>200</code><desc>success</desc>' +
                                '<cart_count>%s</cart_count><cart_price>%s</cart_price><remains>%s</remains></result>'
                                % (request.session['cart_count'], request.session['cart_price'], int(item.count) - int(item.reserved)),
                                mimetype="text/xml")
    else:
        return HttpResponse('<result><code>400</code><desc>it tmust be ajax call</desc></result>', mimetype="text/xml")

def clean_cart(request):
    """
    Функция очистки корзины
    """
    if (request.is_ajax()):
        items = request.session.get('cart_items', {})
        for i in items:
            dbitem = models.Item.objects.get(id=i)
            count = items[i].get('count', 0)
            dbitem.reserved -= count
            dbitem.save()
        init_cart(request)
        return HttpResponse('<result><code>200</code><desc>done</desc></result>', mimetype="text/xml")
    else:
        return HttpResponse('<result><code>300</code><desc>cannot clean cart</desc></result>', mimetype="text/xml")

def show_cart(request):
    """
    Отображение содержимого корзины.
    """
    class CartItem:
        def __init__(self, title, count, price):
            self.title = title
            self.count = count
            self.price = price
            self.cost = count * price
    items = []
    cart = request.session.get('cart_items', {})
    if len(cart) == 0:
        items.append(CartItem("Нет товаров", 0, 0.00))
    else:
        for i in cart:
            record = models.Item.objects.get(id=i)
            items.append(CartItem(record.title, cart[i]['count'], cart[i]['price']))
    return render_to_response('shop-show-cart.html',
                              {'cart_items': items,
                               'cart_count': request.session.get('cart_count', 0),
                               'cart_price': request.session.get('cart_price', 0.00),
                               'cart_show' : 'yes'
                               })

def show_offer(request):
    """
    Отображение формы для ввода данных о покупателе.
    """
    if not 'cart' in request.session or request.session['cart_count'] == 0:
        return HttpResponseRedirect('/shop/')
    # Определяем класс для отображения формы
    class OfferForm(forms.Form):
        fname = forms.CharField(label=ugettext('Last name'), max_length=64,
                                widget=forms.TextInput(attrs={'class':'longitem wideitem'}))
        iname = forms.CharField(label=ugettext('First name'), max_length=64,
                                widget=forms.TextInput(attrs={'class':'longitem wideitem'}))
        oname = forms.CharField(label=ugettext('Second name'), max_length=64,
                                widget=forms.TextInput(attrs={'class':'longitem wideitem'}))
        address = forms.CharField(label=ugettext('Address'), max_length=255,
                                  widget=forms.TextInput(attrs={'class':'longitem wideitem'}))
        city = forms.ModelChoiceField(queryset=models.City.objects.all(),
                                      label=ugettext('City'),
                                      widget=forms.Select(attrs={'class':'longitem wideitem'}))
#         country = forms.ModelChoiceField(queryset=models.Country.objects.all(),
#                                          label=ugettext('Country'), initial=1,
#                                          widget=forms.Select(attrs={'class':'longitem wideitem'}))
        phone = forms.CharField(label=ugettext('Contact phone'), max_length=20,
                                widget=forms.TextInput(attrs={'class':'longitem wideitem'}))
        phonetype = forms.ModelChoiceField(queryset=models.PhoneType.objects.all(),
                                           label=ugettext('Phone type'),
                                           widget=forms.Select(attrs={'class':'longitem wideitem'}))
        email = forms.EmailField(label=ugettext('E-mail'), max_length=75,
                                 widget=forms.TextInput(attrs={'class':'longitem wideitem'}))
        comment = forms.CharField(label=ugettext('Comment'), 
                                  widget=forms.Textarea(attrs={'class':'longitem wideitem'}))
        
    if request.method == 'POST':
        form = OfferForm(request.POST)
        if form.is_valid():
            # обработать форму
            try:
                phone_type = models.PhoneType.objects.get(id=request.POST['phonetype'])
                city = models.City.objects.get(id=request.POST['city'])
                status = models.OrderStatus.objects.get(id=1)
                buyer, created = models.Buyer.objects.get_or_create(lastname = request.POST['fname'],
                                                                    firstname = request.POST['iname'],
                                                                    secondname = request.POST['oname'],
                                                                    address = request.POST['address'],
                                                                    email =  request.POST['email'],
                                                                    city = city)
                phone, created = models.Phone.objects.get_or_create(number = request.POST['phone'],
                                                                    type = phone_type,
                                                                    owner = buyer)
                order, created = models.Order.objects.get_or_create(buyer = buyer,
                                                                    count = request.session.get('cart_count', 0),
                                                                    totalprice = request.session.get('cart_price', 0.00),
                                                                    status = status)
                cart = request.session.get('cart_items', {})
                for i in cart:
                    item = models.Item.objects.get(id=i)
                    orderdetail = models.OrderDetail(order = order,
                                                     item = item,
                                                     count = cart[i]['count'],
                                                     price = cart[i]['price'])
                    orderdetail.save()
                    # резервируем товар
                    item.count -= cart[i]['count']
                    item.save()
                return HttpResponseRedirect('/shop/ordered/')
            except Exception:
                return HttpResponse('bad form data')
        else:
            return HttpResponse('bad form')
    else:
        form = OfferForm(auto_id='field_%s')
        return render_to_response('shop-show-offer.html',
                                  {'form': form,
                                   'cart_count': request.session.get('cart_count', 0),
                                   'cart_price': request.session.get('cart_price', 0.00)
                                   });

def show_ordered(request):
    init_cart(request)
    return render_to_response('shop-show-ordered.html',
                              {'cart_count': request.session.get('cart_count', 0),
                               'cart_price': request.session.get('cart_price', 0.00)
                               });
    
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
    return models.Item.objects.filter(category=category)

def get_currcat_procs(category):
    """Функция возвращает производителей текущей категории."""
    return [l.producer for l in get_currcat_items(category)]
    
def get_sub_cats_items(category):
    """Функция возвращает элементы всех дочерних категорий,
    включая указанную."""
    cats = set(get_sub_cats(category))
    return models.Item.objects.filter(category__in=cats)
