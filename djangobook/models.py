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

    class Admin:
        list_display = ('title', 'datetime')
        ordering = ('-datetime',)

    def __unicode__(self):
        return self.title
    
    def get_absolute_url(self):
        """ This returns the absolute URL for a record. """
        return '/djangobook/news/'
    
class Claims(models.Model):
    ctx_left = models.CharField(max_length=255)
    selected = models.CharField(max_length=255)
    ctx_right = models.CharField(max_length=255)
    comment = models.TextField()
    url = models.URLField(verify_exists=False)
    datetime = models.DateTimeField()

    class Meta:
        verbose_name = _('Claim')
        verbose_name_plural = _('Claims')

    class Admin:
        list_display = ('selected', 'datetime')
        ordering = ('-datetime',)

    def __unicode__(self):
        return self.selected
    
    #def display(self):
    #    return '%s%s%s' % (self.ctx_left, self.selected, self.ctx_right)
    #display.short_description = _('Claim\'s context')

