# -*- coding: utf-8 -*-

import os, sys
import logging
import locale
import codecs

from pyxmpp.all import JID,Iq,Presence,Message,StreamError
from pyxmpp.jabber.client import JabberClient
from pyxmpp.jid import JIDError

# Import and set up Django's settings
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.append('/home/rad/django.engine')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from django.conf import settings
from jabber.models import Message as WebMsg

try:
    botjid = JID(getattr(settings, 'JABBER_ID', None))
except JIDError:
    print "Check JABBER_ID in project's settings file."
    sys.exit(1)

try:
    jids = [JID(x) for x in getattr(settings, 'JABBER_RECIPIENTS', None)]
except TypeError:
    print "Check JABBER_RECIPIENTS in project's settings file."
    sys.exit(1)

class Client(JabberClient):
    """Simple bot (client) example. Uses
    `pyxmpp.jabber.client.JabberClient` class as base. That class
    provides basic stream setup (including authentication) and Service
    Discovery server. It also does server address and port discovery
    based on the JID provided."""

    def __init__(self, jid, password):

        # if bare JID is provided add a resource -- it is required
        if not jid.resource:
            jid=JID(jid.node, jid.domain, "[moiluch.ru]")

        # setup client with provided connection information
        # and identity data
        JabberClient.__init__(self, jid, password,
                disco_name="ClientBot", disco_type="bot")

        # register features to be announced via Service Discovery
        self.disco_info.add_feature("jabber:iq:version")

    def stream_state_changed(self,state,arg):
        """This one is called when the state of stream connecting the
        component to a server changes. This will usually be used to
        let the user know what is going on."""
        #print "*** State changed: %s %r ***" % (state,arg)

    def session_started(self):
        """This is called when the IM session is successfully started
        (after all the neccessery negotiations, authentication and
        authorization).

        That is the best place to setup various handlers for the
        stream.  Do not forget about calling the session_started()
        method of the base class!"""
        JabberClient.session_started(self)

        # set up handlers for supported <iq/> queries
        self.stream.set_iq_get_handler("query","jabber:iq:version",self.get_version)

        # set up handlers for <presence/> stanzas
        self.stream.set_presence_handler("available",self.presence)
        self.stream.set_presence_handler("subscribe",self.presence_control)
        self.stream.set_presence_handler("subscribed",self.presence_control)
        self.stream.set_presence_handler("unsubscribe",self.presence_control)
        self.stream.set_presence_handler("unsubscribed",self.presence_control)

        # set up handler for <message stanza>
        self.stream.set_message_handler("normal",self.message)

    def get_version(self,iq):
        """Handler for jabber:iq:version queries.

        jabber:iq:version queries are not supported directly by PyXMPP, so the
        XML node is accessed directly through the libxml2 API.  This should be
        used very carefully!"""
        iq=iq.make_result_response()
        q=iq.new_query("jabber:iq:version")
        q.newTextChild(q.ns(),"name","Echo component")
        q.newTextChild(q.ns(),"version","1.0")
        self.stream.send(iq)
        return True

    def message(self,stanza):
        """Message handler for the component.

        Echoes the message back if its type is not 'error' or
        'headline', also sets own presence status to the message
        body. Please note that all message types but 'error' will be
        passed to the handler for 'normal' message unless some
        dedicated handler process them.

        :returns: `True` to indicate, that the stanza should not be
        processed any further."""
        subject=stanza.get_subject()
        body=stanza.get_body()
        t=stanza.get_type()
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
            # 'headline' messages should never be replied to
            return True
        if subject:
            subject=u"Re: "+subject

        # save incoming jabber message (from admins)
        msg_admin = WebMsg(nick = 'Mngr', msg = body)
        msg_admin.save()

        messages = WebMsg.objects.filter(is_really_sent=False, client_admin=True).order_by('sent_date')
        for msg in messages:
            #import pdb; pdb.set_trace()
            for j in jids:
                nick, mess = getattr(msg, 'nick'), getattr(msg, 'msg')
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
        """Handle 'available' (without 'type') and 'unavailable' <presence/>."""
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
        print msg

    def presence_control(self,stanza):
        """Handle subscription control <presence/> stanzas -- acknowledge
        them."""
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

        print msg
        p=stanza.make_accept_response()
        self.stream.send(p)
        return True

    def print_roster_item(self,item):
        if item.name:
            name=item.name
        else:
            name=u""
        print (u'%s "%s" subscription=%s groups=%s'
                % (unicode(item.jid), name, item.subscription,
                    u",".join(item.groups)) )

    def roster_updated(self,item=None):
        if not item:
            print u"My roster:"
            for item in self.roster.get_items():
                self.print_roster_item(item)
            return
        print u"Roster item updated:"
        self.print_roster_item(item)

# XMPP protocol is Unicode-based to properly display data received
# _must_ convert it to local encoding or UnicodeException may be raised
locale.setlocale(locale.LC_CTYPE,"")
encoding=locale.getlocale()[1]
if not encoding:
    encoding="us-ascii"
sys.stdout=codecs.getwriter(encoding)(sys.stdout,errors="replace")
sys.stderr=codecs.getwriter(encoding)(sys.stderr,errors="replace")


# PyXMPP uses `logging` module for its debug output
# applications should set it up as needed
logger=logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO) # change to DEBUG for higher verbosity

print u"creating client..."
c=Client(JID(getattr(settings, 'JABBER_ID', None)),
         getattr(settings, 'JABBER_PASSWORD', None))

print u"connecting..."
c.connect()

print u"looping..."
try:
    # Component class provides basic "main loop" for the applitation
    # Though, most applications would need to have their own loop and call
    # component.stream.loop_iter() from it whenever an event on
    # component.stream.fileno() occurs.
    c.loop(1)
except KeyboardInterrupt:
    print u"disconnecting..."
    c.disconnect()

print u"exiting..."
# vi: sts=4 et sw=4
