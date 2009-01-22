# -*- coding: utf-8 -*-

from django.utils.translation import ugettext
from django.utils.translation import gettext_lazy as _
from django.db import models

from datetime import datetime

class News(models.Model):
    title = models.CharField(ugettext(u'Title'), max_length=255)
    text = models.TextField()
    datetime = models.DateTimeField()

    class Meta:
        verbose_name = _(u'News')
        verbose_name_plural = _(u'News')

    def __unicode__(self):
        return self.title
    
    def get_absolute_url(self):
        """ This returns the absolute URL for a record. """
        return '/news/'
    
class Claims(models.Model):
    ctx_left = models.CharField(max_length=255, blank=True)
    selected = models.CharField(max_length=255)
    ctx_right = models.CharField(max_length=255, blank=True)
    comment = models.TextField()
    url = models.URLField(verify_exists=False)
    email = models.EmailField()
    datetime = models.DateTimeField()

    class Meta:
        verbose_name = _(u'Claim')
        verbose_name_plural = _(u'Claims')

    def __unicode__(self):
        return self.selected

    def get_status(self):
        try:
            status = ClaimStatus.objects.filter(claim=self).order_by('-applied')[0].status
        except:
            status = _(u'Unknown')
        return status

    def set_status(self, code):
        status = ClaimStatus(claim=self, status=code,
                             applied=datetime.now())
        status.save()

CLAIM_STATUSES = ((1, _(u'New')), (2, _(u'Assigned')),
                  (3, _(u'Fixed')), (4, _(u'Invalid')))

class ClaimStatus(models.Model):
    claim = models.ForeignKey(Claims)
    status = models.CharField(max_length=1, choices=CLAIM_STATUSES)
    applied = models.DateTimeField()

    class Meta:
        verbose_name = _(u'Claim status')
        verbose_name_plural = _(u'Claim statuses')

    def __unicode__(self):
        return self.status
