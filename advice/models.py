# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

class Text(models.Model):
    weight = models.FloatField(
        verbose_name=_(u'Weight'), 
        help_text=_(u'The weight of an advice.'),
        default=0.0)
    title = models.CharField(
        verbose_name=_(u'Title'), max_length=64)
    desc = models.TextField(
        verbose_name=_(u'Description'),
        help_text=_(u'The description of an advice.'), 
        null=True, blank=True)
    enabled = models.BooleanField(
        verbose_name=_(u'Enabled'),
        help_text=_(u'Is this advice enabled?'),
        default=False)

    class Meta:
        verbose_name = _(u'Text')
        verbose_name_plural = _(u'Texts')

    def __unicode__(self):
        return self.title
