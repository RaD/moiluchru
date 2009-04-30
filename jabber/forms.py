# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext as _

class JabberMessage(forms.Form):
    message = forms.CharField(label=_(u'Message'), max_length=1024)
