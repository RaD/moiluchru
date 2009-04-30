# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import gettext_lazy as _

class Message(models.Model):
    nick = models.CharField(_(u'Nick'), max_length=4) # надеемся, минуты и секунды в качестве ника будут достаточно уникальными
    msg = models.CharField(_(u'Message'), max_length=1024)
    sent_date = models.DateTimeField(verbose_name=_(u'Sent'), auto_now_add=True)
    is_really_sent = models.BooleanField(default=False)
    client_admin = models.BooleanField(default=True)
