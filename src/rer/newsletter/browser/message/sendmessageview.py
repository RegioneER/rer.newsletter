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


KEY = "rer.newsletter.message.details"


class SendMessageView(form.Form):
    ignoreContext = True

    @property
    def success_message(self):
        return _(
            "message_send",
            default="Message sent correctly to ${subscribers} subscribers.",
            mapping=dict(subscribers=self.active_subscriptions),
        )

    @property
    def error_message(self):
        return _(
            "message_send_error",
            default="Unable to send the message to subscribers. "
            "Please contact the site administrator.",
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

    @button.buttonAndHandler(_("send_sendingview", default="Send"))
    def handleSave(self, action):
        res = self.context.send_message()
        status = res.get("status", "")
        message = status == OK and self.success_message or self.error_message
        message_type = status == OK and "info" or "error"
        api.portal.show_message(
            message=message, request=self.request, type=message_type
        )
        self.request.response.redirect(self.context.absolute_url())


message_sending_view = wrap_form(
    SendMessageView, index=ViewPageTemplateFile("templates/sendmessageview.pt")
)
