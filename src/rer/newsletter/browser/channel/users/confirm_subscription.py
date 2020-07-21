# -*- coding: utf-8 -*-
from plone import api
from Products.Five.browser import BrowserView
from rer.newsletter import _
from rer.newsletter.adapter.subscriptions import IChannelSubscriptions
from rer.newsletter.contentrules.events import SubscriptionEvent
from rer.newsletter.contentrules.events import UnsubscriptionEvent
from rer.newsletter.utils import OK
from rer.newsletter.utils import compose_sender
from rer.newsletter.utils import get_site_title
from zope.component import getMultiAdapter
from zope.event import notify

import logging

logger = logging.getLogger(__name__)


class ConfirmSubscription(BrowserView):
    def render(self):
        return self.index()

    def _sendGenericMessage(self, template, receiver, message, message_title):
        mail_template = self.context.restrictedTraverse(
            "@@{0}".format(template)
        )

        parameters = {
            "header": self.context.header,
            "footer": self.context.footer,
            "style": self.context.css_style,
            "portal_name": get_site_title(),
            "channel_name": self.context.title,
        }

        mail_text = mail_template(**parameters)

        portal = api.portal.get()
        mail_text = portal.portal_transforms.convertTo("text/mail", mail_text)

        response_email = compose_sender(self.context)

        # invio la mail ad ogni utente
        mail_host = api.portal.get_tool(name="MailHost")
        mail_host.send(
            mail_text.getData(),
            mto=receiver,
            mfrom=response_email,
            subject=message_title,
            charset="utf-8",
            msg_type="text/html",
        )

        return OK

    def __call__(self):
        secret = self.request.get("secret")
        action = self.request.get("action")

        response = None
        channel = getMultiAdapter(
            (self.context, self.request), IChannelSubscriptions
        )

        if action == u"subscribe":
            response, user = channel.activateUser(secret=secret)
            # mandare mail di avvenuta conferma
            if response == OK:
                notify(SubscriptionEvent(self.context, user))
                self._sendGenericMessage(
                    template="activeuserconfirm_template",
                    receiver=user,
                    message="Messaggio di avvenuta iscrizione",
                    message_title="Iscrizione confermata",
                )
                status = _(
                    u"generic_activate_message_success",
                    default=u'Ti sei iscritto alla newsletter {channel}'
                    ' del portale "{site}".'.format(
                        channel=self.context.title, site=get_site_title()
                    ),
                )

        elif action == u"unsubscribe":
            response, mail = channel.deleteUserWithSecret(secret=secret)
            if response == OK:
                notify(UnsubscriptionEvent(self.context, mail))
                status = _(
                    u"generic_delete_message_success",
                    default=u"Succesfully unsubscribed.",
                )

        if response == OK:
            api.portal.show_message(
                message=status, request=self.request, type=u"info"
            )
        else:
            logger.error(
                'Unable to unsubscribe user with token "{token}" on channel {channel}.'.format(  # noqa
                    token=secret, channel=channel.absolute_url()
                )
            )
            api.portal.show_message(
                message=_(
                    "unable_to_unsubscribe",
                    default=u"Unable to unsubscribe to this channel."
                    u" Please contact site administrator.",
                ),
                request=self.request,
                type=u"error",
            )

        return self.render()
