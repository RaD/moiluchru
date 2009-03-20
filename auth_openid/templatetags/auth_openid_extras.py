# -*- coding: utf-8 -*-
from django import template

from cargo.auth_openid.forms import OpenIDLoginForm

register = template.Library()

@register.inclusion_tag('auth_openid/login_form.html')
def openid_login_form(form_legend=None):
    """
    Return rendered in "p mode" openid login form.
    """

    if form_legend is None:
        form_legend = 'Авторизация через OpenID'
    form = OpenIDLoginForm()#auto_id='%s')
    return {'form': form,
            'form_legend': form_legend
            }
