# -*- coding: utf-8 -*-

from django.utils.translation import gettext_lazy as _
from django.db import models

class Text(models.Model):
    label = models.CharField(_(u'Label'), max_length=32, unique=True)
    reg_date = models.DateTimeField(verbose_name=_(u'Defined'), auto_now_add=True)
    text = models.TextField()

    class Meta:
        verbose_name = _(u'Text')
        verbose_name_plural = _(u'Texts')

    def __unicode__(self):
        return self.label
    
    def get_absolute_url(self):
        """ This returns the absolute URL for a record. """
        return '/text/%s/' % self.label
    
