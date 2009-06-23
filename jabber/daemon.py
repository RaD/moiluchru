#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, time, xmpp
import locale, codecs

# Подключение и настройка среды Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.append('/home/rad/django.engine')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from django.conf import settings
from jabber import models

class Bot:

    def __init__(self, jabber, jid_info, remotejids):
        self.jabber = jabber
        self.remotejids = remotejids
        self.received_messages = []

        jid_str = '%s@%s' % (jid_info.nick, getattr(settings, 'JABBER_SERVER'))
        self.jid = xmpp.protocol.JID(jid_str)
        self.password = jid_info.password

    def register_handlers(self):
        self.jabber.RegisterHandler('message', self.xmpp_message)

    def xmpp_connect(self):
        con=self.jabber.connect()
        if not con:
            sys.stderr.write('could not connect!\n')
            return False
        sys.stderr.write('[%s]: connected with %s\n' % (self.jid, con))
        auth=self.jabber.auth(self.jid.getNode(),
                              self.password,
                              resource=self.jid.getResource())
        if not auth:
            sys.stderr.write('could not authenticate!\n')
            return False
        sys.stderr.write('[%s]: authenticated using %s\n' % (self.jid, auth))
        self.register_handlers()
        return con

    def xmpp_message(self, con, event):
        sys.stderr.write('[%s]: received message\n' % self.jid)
        type = event.getType()
        fromjid = event.getFrom().getStripped()
        if type in ['message', 'chat', None] and fromjid in self.remotejids:
            msg = event.getBody()
            self.received_messages.append(msg)
            sys.stderr.write('[%s]: text is %s\n' % (self.jid, msg))

    def send_message(self, message):
        sys.stderr.write('[%s]: send message\n' % self.jid)
        for recipient in self.remotejids:
            m = xmpp.protocol.Message(to=recipient, body=message, typ='chat')
            self.jabber.send(m)
            sys.stderr.write('[%s]: text is %s\n' % (self.jid, message))
            pass

    def get_received_messages(self, clean=False):
        result = self.received_messages
        if clean:
            self.received_messages = []
        return result

##
## Начало программы
##

# XMPP протокол использует Unicode и для правильного отображения
# полученных данных должен преобразовывать их в локальную кодировку
# или вызывать исключение UnicodeException.

locale.setlocale(locale.LC_CTYPE,"")
encoding=locale.getlocale()[1]
if not encoding:
    encoding="utf-8"
sys.stdout=codecs.getwriter(encoding)(sys.stdout,errors="replace")
sys.stderr=codecs.getwriter(encoding)(sys.stderr,errors="replace")

jabber_pool = {} # {'nick': 'jid_id'}

# Отладка управляется из конфигурации проекта
DEBUG = getattr(settings, 'DEBUG', False)

try:
    admin_jids = [xmpp.protocol.JID(x) for x in getattr(settings, 'JABBER_RECIPIENTS', None)]
except TypeError:
    print "Check JABBER_RECIPIENTS in project's settings file."
    sys.exit(1)

##
## Функции
##

def register_connection(web_nick):
    """ Метод для регистрации нового аккаунта на джаббер сервере. """
    sys.stderr.write('[%s]: register connection\n' % web_nick)
    jid_info = models.JidPool().alloc_jid()

    jid_str = '%s@%s' % (jid_info.nick, getattr(settings, 'JABBER_SERVER'))
    jid = xmpp.protocol.JID(jid_str)
    client = xmpp.Client(jid.getDomain(), debug=[])
        
    bot = Bot(client, jid_info, admin_jids)

    if not bot.xmpp_connect():
        sys.stderr.write("Could not connect to server, or password mismatch!\n")
        sys.exit(1)

    jabber_pool.update({web_nick: (jid_info.id, jid_str, client, bot)})


def create_connection(web_nick, jid_info):
    """ Метод для создания соединения с джаббер сервером. """
    sys.stderr.write('[%s]: create connection\n' % web_nick)
    jid_str = '%s@%s' % (jid_info.nick, getattr(settings, 'JABBER_SERVER'))
    jid = xmpp.protocol.JID(jid_str)
    client = xmpp.Client(jid.getDomain(), debug=[])
        
    bot = Bot(client, jid_info, admin_jids)

    if not bot.xmpp_connect():
        sys.stderr.write("Could not connect to server, or password mismatch!\n")
        sys.exit(1)

    jabber_pool.update({web_nick: (jid_info.id, jid_str, client, bot)})


def process_message(msg):
    """ Для обработки сообщения требуется соединение с джаббер сервером:
    1) оно может быть активным, т.е. лежит в пуле; 2) оно может быть
    зарегистрированным, т.е. надо взять из базы и использовать; 3) его
    нет, т.е. надо пройти оба шага. """

    web_nick = msg.nick
    web_text = msg.msg

    # получаем активное соединение
    if web_nick not in jabber_pool:
        try:
            # соединение надо активировать
            jid_info = models.JidPool.objects.filter(is_locked=False)[0]
            create_connection(web_nick, jid_info)
        except IndexError:
            # надо создать дополнительный аккаунт
            register_connection(web_nick)

    (id, jid_info, client, bot) = jabber_pool[web_nick]

    bot.send_message(web_text)

    msg.is_processed = True
    msg.save()

pool = models.JidPool.objects.filter(id__gt=1, is_locked=True)

def jid_free(pool_object):
    pool_object.is_locked = False
    pool_object.save()

map(jid_free, pool)

print 'Initialized'

while True:
    # проверить наличие сообщений для отправки
    messages = models.Message.objects.filter(is_processed=False, client_admin=True).order_by('sent_date')
    if DEBUG and len(messages) > 0:
        print 'Got %i messages' % len(messages)
    # обработать каждое сообщение
    map(process_message, messages)
    # проверить наличие пришедших сообщений
    for web_nick in jabber_pool.keys():
        (id, jid_info, client, bot) = jabber_pool[web_nick]
        client.Process(1)
        
        received = bot.get_received_messages(True)
        for msg in received:
            m = models.Message(nick=web_nick, msg=msg, client_admin=False)
            m.save()
    # спячка
    time.sleep(1)

for k in jabber_pool.keys():
    (id, jid_info, client, bot) = jabber_pool[k]
    client.disconnect()

sys.exit(0)
