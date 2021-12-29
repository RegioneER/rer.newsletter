# -*- coding: utf-8 -*-
from plone import api
from rer.newsletter import _
from rer.newsletter.adapter.subscriptions import IChannelSubscriptions
from rer.newsletter.contentrules.events import SubscriptionEvent
from rer.newsletter.contentrules.events import UnsubscriptionEvent
from rer.newsletter.utils import OK
from rer.newsletter.utils import compose_sender
from rer.newsletter.utils import get_site_title
from zope.component import getMultiAdapter
from zope.event import notify
from plone import api
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from rer.newsletter import _
from rer.newsletter import logger
from rer.newsletter.adapter.subscriptions import IChannelSubscriptions
from six import PY2
from zope.component import getMultiAdapter

import logging


logger = logging.getLogger(__name__)


class NewsletterConfirmSubscription(Service):

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

    def reply(self):
        data = json_body(self.request)
        secret = data.get("secret")
        action = data.get("action")
        error = None
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
                status = u"generic_activate_message_success"

        elif action == u"unsubscribe":
            response, mail = channel.deleteUserWithSecret(secret=secret)
            if response == OK:
                notify(UnsubscriptionEvent(self.context, mail))
                status = u"generic_delete_message_success"

        if response != OK:
            logger.error(
                'Unable to unsubscribe user with token "{token}" on channel {channel}.'.format(  # noqa
                    token=secret, channel=channel.absolute_url()
                )
            )
            error = u"unable_to_unsubscribe"

        return {
            "@id": self.request.get("URL"),
            "status": status if not error else u'error',
            "errors": error if error else None,
        }