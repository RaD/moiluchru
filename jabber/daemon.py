#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import threading, Queue
import time

import logging
import locale
import codecs

from pyxmpp.all import JID,Iq,Presence,Message,StreamError
from pyxmpp.jabber.client import JabberClient
from pyxmpp.jid import JIDError

# Подключение и настройка среды Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.append('/home/rad/django.engine')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from django.conf import settings
from jabber import models

# Отладка управляется из конфигурации проекта
DEBUG = getattr(settings, 'DEBUG', False)

try:
    admin_jids = [JID(x) for x in getattr(settings, 'JABBER_RECIPIENTS', None)]
except TypeError:
    print "Check JABBER_RECIPIENTS in project's settings file."
    sys.exit(1)

##
## Класс потока для джаббер клиента
## TODO: продумать как оно будет ловить сигнал Die
##
class JabberThread(threading.Thread):
    """ Класс потока для джаббер клиента. """
    def __init__(self, client, queue_wj, queue_jw, register=False):
        self.client = client
        self.queue_web_jabber = queue_wj
        self.queue_jabber_web = queue_jw
        self.register = register
        self.die = False

    def run(self):
        """ Код потока. """
        if DEBUG:
            print u"connecting..."
        self.client.connect(self.register)

        if DEBUG:
            print u"looping..."
        
        while not self.die:
            self.client.loop(1)

        if DEBUG:
            print u"disconnecting..."
        self.client.disconnect()

##
## Класс джаббер клиента
##
class Client(JabberClient):
    """ Простой джаббер клиент, который предоставляет базовую настройку
    соединения, включая аутентификацию и поиск сервисов. Также
    производится поиска адреса и порта сервера по предоставленному
    идентификатору. """

    def __init__(self, jid, password):

        # обязательно надо указывать resource
        if not jid.resource:
            jid=JID(jid.node, jid.domain, "[moiluch.ru]")

        # настроить клиента по переданной информации
        JabberClient.__init__(self, jid, password,
                              disco_name="WebBot", disco_type="bot")

        # регистрируем свойства, которые будут доступны через локатор сервисов
        self.disco_info.add_feature("jabber:iq:version")

    def stream_state_changed(self,state,arg):
        """ Метод вызывается при изменении состояния соединения. Обычно
        используется для уведомления пользователя о данном событии. """
        #print "*** State changed: %s %r ***" % (state,arg)

    def session_started(self):
        """ Метод вызывается при успешном установлении соединения (после всех
        необходимых "обнюхиваний", аутентификаций и авторизаций.

        Является лучшим местом для настройки разнообразных
        обработчиков для потока. Не забудьте вызвать данный метод
        базового класса! """

        JabberClient.session_started(self)

        # установка обработчика для <iq/> запросов
        self.stream.set_iq_get_handler("query","jabber:iq:version",self.get_version)

        # установка обработчиков для <presence/> stanzas
        self.stream.set_presence_handler("available",self.presence)
        self.stream.set_presence_handler("subscribe",self.presence_control)
        self.stream.set_presence_handler("subscribed",self.presence_control)
        self.stream.set_presence_handler("unsubscribe",self.presence_control)
        self.stream.set_presence_handler("unsubscribed",self.presence_control)

        # установка обработчика для <message stanza>
        self.stream.set_message_handler("normal",self.message)

    def get_version(self,iq):
        """ Обработчик для jabber:iq:version запросов.

        jabber:iq:version запросы не поддерживаются напрямую
        библиотекой PyXMPP, следовательно соответствующий XML узел
        обрабатывается напрямую через libxml2 API. Этим надо
        пользоваться очень аккуратно! """
        iq=iq.make_result_response()
        q=iq.new_query("jabber:iq:version")
        q.newTextChild(q.ns(),"name","WebJabber component")
        q.newTextChild(q.ns(),"version","1.0")
        self.stream.send(iq)
        return True

    def message(self,stanza):
        """ Обработчик сообщений.

        Отправляет принятые сообщения обратно, в случае если они не
        принадлежат к типам 'error' или 'headline', также
        устанавливает собственный статус активности в теле
        сообщения. Следует помнить, что все типы сообщений, кроме
        'error' будут передаваться данному обработчику до тех пор,
        пока не будут созданы соответствующие обработчика для таких
        типов сообщений.

        :возвращает: `True` для того, чтобы указать, что данное
        сообщение больше не надо обрабатывать. """
        subject=stanza.get_subject()
        body=stanza.get_body()
        t=stanza.get_type()
        if DEBUG:
            print u'Message from %s received.' % (unicode(stanza.get_from(),)),
            if subject:
                print u'Subject: "%s".' % (subject,),
            if body:
                print u'Body: "%s".' % (body,),
            if t:
                print u'Type: "%s".' % (t,)
            else:
                print u'Type: "normal".' % (t,)
        if stanza.get_type()=="headline":
            # сообщения типа 'headline' никогда не надо отправлять обратно
            return True
        if subject:
            subject=u"Re: "+subject

        # сохраняем в базу данных сообщение пришедшее от администраторов
        try:
            jid_admin = JidPool.objects.get(nick='admins')
            msg_admin = WebMsg(jid=jid_admin, msg=body)
            msg_admin.save()
        except JidPool.DoesNotExist:
            if DEBUG:
                print "Install Administrators' JID into jabber_jidpool table."
            sys.exit(1)

        messages = WebMsg.objects.filter(is_really_sent=False).order_by('sent_date')
        for msg in messages:
            #import pdb; pdb.set_trace()
            for j in jids:
                nick, mess = getattr(msg, 'nick'), getattr(msg, 'msg')
                if DEBUG:
                    print j, nick, mess
                m=Message(to_jid=j, from_jid=botjid, stanza_type='message',
                          subject=nick, body=msg)
                self.stream.send(m)
                if body:
                    p=Presence(status=body)
                    self.stream.send(p)
            msg.is_really_sent = True
            msg.save()
        return True

    def presence(self,stanza):
        """ Обработчик для 'available' (без 'type') и 'unavailable' <presence/>."""
        msg=u"%s has become " % (stanza.get_from())
        t=stanza.get_type()
        if t=="unavailable":
            msg+=u"unavailable"
        else:
            msg+=u"available"

        show=stanza.get_show()
        if show:
            msg+=u"(%s)" % (show,)

        status=stanza.get_status()
        if status:
            msg+=u": "+status
        if DEBUG:
            print msg

    def presence_control(self,stanza):
        """ Обработчик для управления подпиской на <presence/> stanzas --
        acknowledge them."""
        msg=unicode(stanza.get_from())
        t=stanza.get_type()
        if t=="subscribe":
            msg+=u" has requested presence subscription."
        elif t=="subscribed":
            msg+=u" has accepted our presence subscription request."
        elif t=="unsubscribe":
            msg+=u" has canceled his subscription of our."
        elif t=="unsubscribed":
            msg+=u" has canceled our subscription of his presence."

        if DEBUG:
            print msg
        p=stanza.make_accept_response()
        self.stream.send(p)
        return True

    def print_roster_item(self,item):
        if item.name:
            name=item.name
        else:
            name=u""
        if DEBUG:
            print (u'%s "%s" subscription=%s groups=%s'
                   % (unicode(item.jid), name, item.subscription,
                      u",".join(item.groups)) )

    def roster_updated(self,item=None):
        if not item:
            if DEBUG:
                print u"My roster:"
            for item in self.roster.get_items():
                self.print_roster_item(item)
            return
        if DEBUG:
            print u"Roster item updated:"
        self.print_roster_item(item)

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


# PyXMPP использует модуль logging для записи отладочных сообщений.

logger=logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO) # change to DEBUG for higher verbosity

thread_pool = {} # {'nick': 'jid_id'}
message_pool_wj = Queue.Queue(0) # web to jabber
message_pool_jw = Queue.Queue(0) # jabber to web
#shared_look = threading.Lock()

##
## Функции
##

def process_message(msg):
    nick = msg.nick
    text = msg.msg

    try:
        jid_id = thread_pool[nick]
        if DEBUG:
            print 'Got JID from pool'
    except KeyError:
        if DEBUG:
            print 'Register new JID'
        model = models.JidPool()
        jid = model.alloc_jid()
        jid_id = jid.id
        try:
            client = Client(JID('%s@%s' % (jid.nick, getattr(settings, 'JABBER_SERVER'))),
                            jid.password)
            thread = JabberThread(client, message_pool_wj, message_pool_jw, True)
            runner = threading.Thread(None, thread.run)
            thread_pool.update({nick: jid_id})
            runner.start()
        except Exception, e:
            print e
            sys.exit(1)

if DEBUG:
    print 'Looping'
while True:
    # получить сообщения для отправки
    messages = models.Message.objects.filter(is_processed=False, client_admin=True).order_by('sent_date')
    if DEBUG:
        print 'Got %i messages' % len(messages)
    # обработать каждое сообщение
    map(process_message, messages)
    # спячка
    if DEBUG:
        print '.',
    time.sleep(5)

sys.exit(0)
