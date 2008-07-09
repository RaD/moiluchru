# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.utils.translation import ugettext, gettext_lazy as _
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.core import validators
from django import newforms as forms
from django.contrib import auth
from cargo.shop import models

def login(request):
    """
    Функция для отображения страницы для ввода логина.
    """
    # Класс для формы логина
    class LoginForm(forms.Form):
        login = forms.CharField(label=ugettext('Login'), max_length=30,
                                widget=forms.TextInput(attrs={'class':'longitem wideitem'}))
        passwd = forms.CharField(label=ugettext('Password'), max_length=128,
                                 widget=forms.PasswordInput(attrs={'class':'longitem wideitem'}))

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            try:
                login = request.POST['login']
                passwd = request.POST['passwd']
                user = auth.authenticate(username=login, password=passwd)
                if user is not None and user.is_active:
                    auth.login(request, user)
                    return HttpResponseRedirect("/shop/manager/orders/active/")
                else:
                    return render_to_response('manager-login.html',
                                              {'form': form, 'panel_hide': 'yes',
                                               'login_error': 'Возможно, вы неправильно указали данные.'})
                    return HttpResponseRedirect("/shop/manager/")
            except Exception:
                return HttpResponse('bad form data')
        else:
            return HttpResponse('bad form')
    else:
        if not request.session.test_cookie_worked():
            request.session.set_test_cookie()
        form = LoginForm(auto_id='field_%s')
        return render_to_response('manager-login.html', {'form': form, 'panel_hide': 'yes'})

