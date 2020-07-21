# -*- coding: utf-8 -*-
from plone import api
from plone.memoize.view import memoize
from plone.z3cform.layout import wrap_form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from rer.newsletter import _
from rer.newsletter.adapter.sender import IChannelSender
from rer.newsletter.adapter.subscriptions import IChannelSubscriptions
from rer.newsletter.content.channel import Channel
from rer.newsletter.utils import OK
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
    def success_message(self):
        return _(
            u'message_send',
            default=u'Message sent correctly to ${subscribers} subscribers.',
            mapping=dict(subscribers=self.active_subscriptions),
        )

    @property
    def error_message(self):
        return _(
            u'message_send_error',
            default=u'Unable to send the message to subscribers. '
            u'Please contact the site administrator.',
        )

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
                status = self.send_syncronous()
        else:
            # invio sincrono del messaggio
            status = self.send_syncronous()
        message = status == OK and self.success_message or self.error_message
        type = status == OK and u'info' or u'error'
        api.portal.show_message(
            message=message, request=self.request, type=type
        )
        self.request.response.redirect(self.context.absolute_url())

    def send_syncronous(self):
        adapter = getMultiAdapter((self.channel, self.request), IChannelSender)
        return adapter.sendMessage(message=self.context)


message_sending_view = wrap_form(
    SendMessageView, index=ViewPageTemplateFile('templates/sendmessageview.pt')
)
