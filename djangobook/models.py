from django.utils.translation import ugettext
from django.utils.translation import gettext_lazy as _
from django.db import models

class News(models.Model):
    title = models.CharField(ugettext('Title'), max_length=255)
    text = models.TextField()
    datetime = models.DateTimeField()

    class Meta:
        verbose_name = _('News')
        verbose_name_plural = _('News')

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
        verbose_name = _('Claim')
        verbose_name_plural = _('Claims')

    def __unicode__(self):
        return self.selected
