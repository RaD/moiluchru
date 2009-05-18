# -*- coding: utf-8 -*-

from django.http import Http404
from django.utils.translation import gettext_lazy as _

from text.models import Text

def text(request, label=None):
    try:
        o = Text.objects.get(label=label)
        return o.text
    except Text.DoesNotExist:
        raise Http404
