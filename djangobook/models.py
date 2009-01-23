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

    def get_description(self, code):
        for i in CLAIM_STATUSES:
            if int(i[0]) == int(code):
                return i[1]
        return _(u'Unknown')

    def sendemail(self, code):
        from email.MIMEText import MIMEText
        from email.MIMEMultipart import MIMEMultipart

        mail_from = 'rad@caml.ru'
        mail_to = self.email
        mail_subject = '%s %s' % (_(u'DjangoBook in russian: Claim\'s state was changed to'),
                                  self.get_description(code))
        msgRoot = MIMEMultipart('related')
        msgRoot.set_charset('UTF-8')
        msgRoot['From'] = mail_from
        msgRoot['To'] = mail_to
        msgRoot['Subject'] = mail_subject
        msgRoot['Mime-version'] = '1.0'
        msgRoot['Content-type'] = 'text/plain; charset=utf-8'
        msgRoot['Content-transfer-encoding'] = '8bit'
        msgRoot.preamble = u'This is a multi-part message in MIME format.'.encode('utf-8')
        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)
        msgText = MIMEText(_(u'This is automatic generated message, you do not need to answer on it.'))
        msgAlternative.attach(msgText)

        import smtplib
        smtp = smtplib.SMTP()
        smtp.connect('localhost')
        smtp.sendmail(mail_from, mail_to, msgRoot.as_string())
        smtp.quit()

    def get_status(self):
        try:
            status = ClaimStatus.objects.filter(claim=self).order_by('-applied')[0].status
        except:
            status = None
        return status

    def set_status(self, code):
        self.save() # it is very important
        try:
            status_old = ClaimStatus.objects.filter(claim=self).order_by('-applied')[0]
        except:
            status_old = None
        status = ClaimStatus(claim=self, status=code, applied=datetime.now())
        # there is no previous status or there is but with different status code, then save it
        if not status_old or status_old and status_old.status != code:
            status.save()
            self.sendemail(code)

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
