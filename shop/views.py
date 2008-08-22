# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.utils.translation import ugettext, gettext_lazy as _
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.db.models import Q
from django.template import RequestContext
from django.core.paginator import Paginator
from django import newforms as forms
from django.newforms.util import ErrorList
from cargo import settings
from cargo.shop import models, common

def cart_ctx_proc(request):
    """
    Контекстный процессор для заполнения данных о корзине.
    """
    return {'site_name': settings.SITE_NAME,
            'howtos': models.Howto.objects.all(),
            'top_cats': models.Category.objects.filter(parent__isnull=True),
            'cart_count': request.session.get('cart_count', 0),
            'cart_price': request.session.get('cart_price', 0.00)}

def show_main_page(request):
    """
    Функция для отображения главной страницы сайта.
    Осуществляем проверку поддержки Cookie.
    """
    if request.session.test_cookie_worked():
        #request.session.delete_test_cookie()
        common.does_cart_exist(request)
    else:
        request.session.set_test_cookie()
    return render_to_response('shop-main.html',
                              {'items': models.Item.objects.order_by('-buys')[:3]},
                              context_instance=RequestContext(request, processors=[cart_ctx_proc]))
    
def show_howto_page(request, howto):
    """
    Функция для отображения вспомогательной информации.
    """
    common.does_cart_exist(request)
    last_page = request.META.get('HTTP_REFERER', '#')
    h = models.Howto.objects.get(id=howto)
    return render_to_response('shop-howto.html', {'howto': h, 'back_to': last_page},
                              context_instance=RequestContext(request, processors=[cart_ctx_proc]))

def search_results(request, page=1):
    """
    Функция для результатов поиска по магазину.
    """
    if request.method == 'POST':
        # TODO: проверить ввод
        userinput = request.POST.get('searchthis', None)
        howmuch = request.POST.get('howmuch', settings.SHOP_ITEMS_PER_PAGE)
        if howmuch == 2:
            item_per_page = 10
        elif howmuch == 3:
            item_per_page = 25
        elif howmuch == 4:
            item_per_page = 50
        else:
            item_per_page = 4
        if userinput:
            i = models.Item.objects.filter(Q(title__search=userinput) |
                                           Q(desc__search=userinput))
            common.does_cart_exist(request)
            p = Paginator(i, item_per_page)
            return render_to_response('shop-search.html',
                                      {'items': p.page(page).object_list,
                                       'search_query': userinput,
                                       'page': p.page(page), 'page_range': p.page_range},
                                      context_instance=RequestContext(request, processors=[cart_ctx_proc]))
        else:
            raise Http404()
    else:
        return HttpResponseRedirect('/shop/')

def show_category_page(request, category, page=1):
    """
    Функция для отображения подчинённых категорий.
    """
    common.does_cart_exist(request)
    i = common.get_currcat_items(category)
    c = models.Category.objects.get(id=category)
    if not i:
        i = common.get_sub_cats_items(c)
        subitems = 'exist'
    else:
        subitems = None
    p = Paginator(i, settings.SHOP_ITEMS_PER_PAGE)
    return render_to_response('shop-category.html',
                              {'parent_cats': common.get_parent_cats(c),
                               'currentcat': c,
                               'producers': common.get_currcat_procs(c),
                               'url': c.get_absolute_url(),
                               'items': p.page(page).object_list,
                               'subitems': subitems,
                               'page': p.page(page), 'page_range': p.page_range},
                              context_instance=RequestContext(request, processors=[cart_ctx_proc]))

def show_producer_page(request, producer, category, page=1):
    """
    Функция для отображения подчинённых категорий для данного производителя.
    """
    common.does_cart_exist(request)
    c = models.Category.objects.get(id=category)
    p = models.Producer.objects.get(id=producer)
    i = common.get_currcat_items(c, p)
    paginator = Paginator(i, settings.SHOP_ITEMS_PER_PAGE)
    return render_to_response('shop-category.html',
                              {'parent_cats': common.get_parent_cats(c),
                               'currentcat': c,
                               'currentproc': p,
                               'categories': c.category_set.all(),
                               'producers': common.get_currcat_procs(c),
                               'url': '/shop/producer/%s/%s/' % (producer, category),
                               'items': paginator.page(page).object_list,
                               'page': paginator.page(page), 'page_range': paginator.page_range},
                              context_instance=RequestContext(request, processors=[cart_ctx_proc]))

def show_item_page(request, item):
    """
    Отображение информации о товаре.
    """
    common.does_cart_exist(request)
    curr_item = models.Item.objects.get(id=item)
    return render_to_response('shop-item.html',
                              {'item': curr_item,
                               'item_remains': curr_item.count - curr_item.reserved,
                               'js_onload': 'show_item_count_info(%s);' % item,
                               'parent_cats': common.get_parent_cats(curr_item.category)},
                              context_instance=RequestContext(request, processors=[cart_ctx_proc]))
    
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
    return render_to_response('shop-cart.html',
                              {'cart': cart, # для отключения кнопок
                               'cart_items': items,
                               'cart_show' : 'yes',
                               'categories': models.Category.objects.filter(parent__isnull=True)},
                              context_instance=RequestContext(request, processors=[cart_ctx_proc]))

def show_offer(request):
    """
    Отображение формы для ввода данных о покупателе.
    Обработка пользовательского ввода.
    """
    if not 'cart_items' in request.session or request.session['cart_count'] == 0:
        return HttpResponseRedirect('/shop/')
    # Определяем класс для отображения ошибок в пользовательском вводе
    class DivErrorList(ErrorList):
        def __unicode__(self):
            return self.as_divs()
        def as_divs(self):
            if not self: return u''
            return u'<div class="errorlist">%s</div>' % ''.join([u'<div class="error">%s</div>' % e for e in self])
    # Определяем класс для отображения формы
    class OfferForm(forms.Form):
        fname = forms.CharField(label=ugettext('Last name'), max_length=64,
                                widget=forms.TextInput(attrs={'class':'longitem'}))
        iname = forms.CharField(label=ugettext('First name'), max_length=64,
                                widget=forms.TextInput(attrs={'class':'longitem'}))
        oname = forms.CharField(label=ugettext('Second name'), max_length=64,
                                widget=forms.TextInput(attrs={'class':'longitem'}))
        address = forms.CharField(label=ugettext('Address'), max_length=255,
                                  widget=forms.TextInput(attrs={'class':'longitem'}))
        city = forms.ModelChoiceField(queryset=models.City.objects.all(),
                                      label=ugettext('City'),
                                      widget=forms.Select(attrs={'class':'longitem'}))
        phone = forms.CharField(label=ugettext('Contact phone'), max_length=20,
                                widget=forms.TextInput(attrs={'class':'longitem'}))
        phonetype = forms.ModelChoiceField(queryset=models.PhoneType.objects.all(),
                                           label=ugettext('Phone type'),
                                           widget=forms.Select(attrs={'class':'longitem'}))
        email = forms.EmailField(label=ugettext('E-mail'), max_length=75,
                                 widget=forms.TextInput(attrs={'class':'longitem'}))
        comment = forms.CharField(label=ugettext('Comment'), required=False,
                                  widget=forms.Textarea(attrs={'class':'longitem'}))
        
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
            return render_to_response('shop-offer.html',
                                      {'form': form, 'cart_show' : 'yes'},
                                      context_instance=RequestContext(request, processors=[cart_ctx_proc]));
    else:
        form = OfferForm(auto_id='field_%s')
        return render_to_response('shop-offer.html',
                                  {'form': form, 'cart_show' : 'yes'},
                                  context_instance=RequestContext(request, processors=[cart_ctx_proc]));

def show_ordered(request):
    common.init_cart(request)
    return render_to_response('shop-ordered.html',{},
                              context_instance=RequestContext(request, processors=[cart_ctx_proc]));
    
