# -*- coding: utf-8 -*-

from django.db import models

from django.utils.translation import ugettext_lazy as _

class Template(models.Model):
    """ Имена файлов с шаблонами, к которым имеется доступ через интерфейс
    администратора. """
    name = models.CharField(max_length=64)
    content = models.TextField(verbose_name=_(u'Content'))
    last_modification = models.DateTimeField(verbose_name=_(u'Last modification'), 
                                             auto_now_add=True, auto_now=True)

    class Meta:
        verbose_name = _(u'Template')
        verbose_name_plural = _(u'Templates')
