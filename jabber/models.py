# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import get_hexdigest

class JidPool(models.Model):
    """ Модель для хранения пула зарегистрированных адресов."""
    nick = models.CharField(_(u'Nick'), max_length=6, default="ml0000")
    password = models.CharField(_(u'Password'), max_length=51, default="sha1$12345$0000000000000000000000000000000000000000")
    is_locked = models.BooleanField(default=False)
    created = models.DateTimeField(verbose_name=_(u'Created'), auto_now_add=True)
    last_used = models.DateTimeField(verbose_name=_(u'Last usage'), auto_now_add=True, auto_now=True)

    def alloc_jid(self):
        """ Метод для выделения свободного идентификатора, если свободных нет,
        то создаётся дополнительный. """
        jid_unlocked = JidPool.objects.filter(is_locked=False)
        jids_count = len(jid_unlocked)
        if jids_count > 0:
            allocated_jid = jid_unlocked[0]
            allocated_jid.is_locked = True
            allocated_jid.save()
            return allocated_jid
        else:
            return self.create_jid()

    def free_jid(self, jid):
        """ Метод для освобождения занятого идентификатора. """
        jid.is_locked = False
        jid.save()

    def create_jid(self):
        """ Метод для создания идентификатора. """
        jids_count = JidPool.objects.count()
        self.nick = 'ml%04d' % int(jids_count + 1)
        self.password = self.generate_password()
        self.is_locked = True
        self.save(force_insert=True)
        return self

    def generate_password(self):
        """ Метод для генерации пароля. """
        import random
        algo = 'sha1'
        salt = get_hexdigest(algo, str(random.random()), str(random.random()))[:5]
        hsh = get_hexdigest(algo, salt, str(random.random()))
        return '%s$%s$%s' % (algo, salt, hsh)

class Message(models.Model):
    """ Модель для хранения сообщений. """
    nick = models.CharField(_(u'Nick'), max_length=6)
    msg = models.CharField(_(u'Message'), max_length=1024)
    sent_date = models.DateTimeField(verbose_name=_(u'Sent'), auto_now_add=True)
    is_really_sent = models.BooleanField(default=False)
    client_admin = models.BooleanField(default=True)
