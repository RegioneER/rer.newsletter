# -*- coding: utf-8 -*-
from plone import api
from plone.memoize.view import memoize
from plone.z3cform.layout import wrap_form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from rer.newsletter import _
from rer.newsletter.adapter.sender import IChannelSender
from rer.newsletter.adapter.subscriptions import IChannelSubscriptions
from rer.newsletter.content.channel import Channel
from six.moves.urllib.parse import urlencode
from z3c.form import button
from z3c.form import form
from zope.component import getMultiAdapter
from zope.component import queryUtility

try:
    from collective.taskqueue.interfaces import ITaskQueue
    from rer.newsletter.queue.handler import QUEUE_NAME
    from rer.newsletter.queue.interfaces import IMessageQueue

    HAS_TASKQUEUE = True
except ImportError:
    HAS_TASKQUEUE = False


KEY = 'rer.newsletter.message.details'


class SendMessageView(form.Form):

    ignoreContext = True

    @property
    @memoize
    def channel(self):
        for obj in self.context.aq_chain:
            if isinstance(obj, Channel):
                return obj
        return None

    @property
    @memoize
    def active_subscriptions(self):
        channel = getMultiAdapter(
            (self.channel, self.request), IChannelSubscriptions
        )
        return channel.active_subscriptions

    @button.buttonAndHandler(_('send_sendingview', default='Send'))
    def handleSave(self, action):

        if HAS_TASKQUEUE:
            messageQueue = queryUtility(IMessageQueue)
            isQueuePresent = queryUtility(ITaskQueue, name=QUEUE_NAME)
            if isQueuePresent is not None and messageQueue is not None:
                # se non riesce a connettersi con redis allora si spacca
                messageQueue.start(self.context)
            else:
                # invio sincrono del messaggio
                self.send_syncronous()
        else:
            # invio sincrono del messaggio
            self.send_syncronous()

        # cambio di stato dopo l'invio
        # api.content.transition(obj=self.context, transition='send')

        # self.request.response.redirect('view')
        self.request.response.redirect(
            '@@send_success_view?'
            + urlencode({'active_users': self.active_subscriptions})
        )
        api.portal.show_message(
            message=_(
                u'message_send',
                default=u'Il messaggio è stato '
                'inviato a {0} iscritti al canale'.format(
                    self.active_subscriptions
                ),
            ),
            request=self.request,
            type=u'info',
        )

    def send_syncronous(self):

        adapter = getMultiAdapter((self.channel, self.request), IChannelSender)
        adapter.sendMessage(message=self.context)


message_sending_view = wrap_form(
    SendMessageView, index=ViewPageTemplateFile('templates/sendmessageview.pt')
)
