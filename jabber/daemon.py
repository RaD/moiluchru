#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, time, xmpp

try:
    if sys.argv[1] == '-d':
        import daemonize
        daemonize.createDaemon()
except IndexError:
    pass

# Подключение и настройка среды Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.append('/home/rad/django.engine')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from django.conf import settings
from jabber import models

# XMPP протокол использует Unicode и для правильного отображения
# полученных данных должен преобразовывать их в локальную кодировку
# или вызывать исключение UnicodeException.

import locale, codecs
locale.setlocale(locale.LC_CTYPE,"")
encoding=locale.getlocale()[1]
if not encoding:
    encoding="utf-8"
sys.stdout=codecs.getwriter(encoding)(sys.stdout,errors="replace")
sys.stderr=codecs.getwriter(encoding)(sys.stderr,errors="replace")

import logging
logging.basicConfig(level=logging.DEBUG,
                    filename='/tmp/moiluch.daemon.log', filemode='a')

class Bot:

    def __init__(self, jabber, web_nick, remotejids):
        self.jabber = jabber
        self.web_nick = web_nick
        self.remotejids = remotejids
        self.received_messages = []

        self.jid = xmpp.protocol.JID(getattr(settings, 'JABBER_ID'))
        self.password = getattr(settings, 'JABBER_PASSWORD')

    def register_handlers(self):
        self.jabber.RegisterHandler('message', self.xmpp_message)

    def xmpp_connect(self):
        con=self.jabber.connect()
        if not con:
            logging.debug('[%s/%s]: could not connect!' % (self.jid, self.password))
            return False
        logging.debug('[%s]: connected with %s\n' % (self.jid, con))
        auth=self.jabber.auth(self.jid.getNode(),
                              self.password,
                              resource='%s[%s]' % ('moiluch.ru', self.web_nick))
        if not auth:
            logging.debug('[%s]: could not authenticate!' % self.jid)
            return False

        # рассказываем всем, что мы в онлайне
        self.jabber.sendInitPresence(1)
        init_p = xmpp.protocol.Presence(status="I'm little bot", show='online')
        self.jabber.send(init_p)

        logging.debug('[%s]: authenticated using %s' % (self.jid, auth))
        self.register_handlers()
        return con

    def xmpp_message(self, con, event):
        logging.debug('[%s]: received message\n' % self.jid)
        type = event.getType()
        fromjid = event.getFrom().getStripped()
        if type in ['message', 'chat', None] and fromjid in self.remotejids:
            msg = event.getBody()
            self.received_messages.append(msg)
            logging.debug('[%s]: text is %s\n' % (self.jid, msg))

    def send_message(self, message):
        logging.debug('[%s]: send message\n' % self.jid)
        for recipient in self.remotejids:
            m = xmpp.protocol.Message(to=recipient, body=message, typ='chat')
            self.jabber.send(m)
            logging.debug('[%s]: text is %s\n' % (self.jid, message))
            pass

    def get_received_messages(self, clean=False):
        result = self.received_messages
        if clean:
            self.received_messages = []
        return result

##
## Функции
##

jabber_pool = {}

def create_connection(web_nick):
    """ Метод для создания соединения с джаббер сервером. """
    sys.stderr.write('[%s]: create connection\n' % web_nick)
    jid = xmpp.protocol.JID(getattr(settings, 'JABBER_ID'))
    client = xmpp.Client(jid.getDomain(), debug=['all'])
        
    bot = Bot(client, web_nick, admin_jids)

    if not bot.xmpp_connect():
        sys.stderr.write("Could not connect to server, or password mismatch!\n")
        sys.exit(1)

    jabber_pool.update({web_nick: (client, bot)})

def process_message(msg):
    """ Для обработки сообщения требуется соединение с джаббер сервером:
    1) оно может быть активным, т.е. лежит в пуле; 2) оно может быть
    зарегистрированным, т.е. надо взять из базы и использовать; 3) его
    нет, т.е. надо пройти оба шага. """

    web_nick = msg.nick
    web_text = msg.msg

    # получаем активное соединение
    if web_nick not in jabber_pool:
        # соединение надо активировать
        create_connection(web_nick)

    (client, bot) = jabber_pool[web_nick]

    bot.send_message(web_text)

    msg.is_processed = True
    msg.save()

try:
    admin_jids = [xmpp.protocol.JID(x) for x in getattr(settings, 'JABBER_RECIPIENTS', None)]
except TypeError:
    print "Check JABBER_RECIPIENTS in project's settings file."
    sys.exit(1)

create_connection('main')
(client, bot) = jabber_pool['main']
roster = client.getRoster()

print 'Initialized'

try:
    while True:
        # проверить наличие сообщений для отправки
        messages = models.Message.objects.filter(is_processed=False, client_admin=True).order_by('sent_date')
        # обработать каждое сообщение
        map(process_message, messages)
        # проверить наличие пришедших сообщений
        for web_nick in jabber_pool.keys():
            (client, bot) = jabber_pool[web_nick]
            client.Process(1)
        
            received = bot.get_received_messages(True)
            for msg in received:
                m = models.Message(nick=web_nick, msg=msg, client_admin=False)
                m.save()
        # спячка
        time.sleep(1)
except KeyboardInterrupt:
    for k in jabber_pool.keys():
        (client, bot) = jabber_pool[k]
        client.disconnect()

sys.exit(0)
