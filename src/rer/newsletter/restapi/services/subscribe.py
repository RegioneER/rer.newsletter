# -*- coding: utf-8 -*-
from plone import api
from plone.protect import interfaces
from plone.protect.authenticator import createToken
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from rer.newsletter import logger
from rer.newsletter.adapter.subscriptions import IChannelSubscriptions
from rer.newsletter.utils import compose_sender
from rer.newsletter.utils import get_site_title
from rer.newsletter.utils import SUBSCRIBED
from rer.newsletter.utils import UNHANDLED
from six import PY2
from zope.component import getMultiAdapter
from zope.interface import alsoProvides


class NewsletterSubscribe(Service):
    def getData(self, data):
        errors = []
        if not data.get("email", None):
            errors.append("invalid_email")
        return {
            "email": data.get("email", None),
        }, errors

    def handleSubscribe(self, postData):
        status = UNHANDLED
        data, errors = self.getData(postData)

        if errors:
            return data, errors

        email = data.get("email", "").lower()

        if self.context.is_subscribable:
            channel = getMultiAdapter(
                (self.context, self.request), IChannelSubscriptions
            )
            status, secret = channel.subscribe(email)

        if status == SUBSCRIBED:
            # creo il token CSRF
            token = createToken()

            # mando mail di conferma
            url = self.context.absolute_url()
            url += "/confirm-subscription?secret=" + secret
            url += "&_authenticator=" + token
            url += "&action=subscribe"

            mail_template = self.context.restrictedTraverse(
                "@@activeuser_template"
            )

            parameters = {
                "title": self.context.title,
                "header": self.context.header,
                "footer": self.context.footer,
                "style": self.context.css_style,
                "activationUrl": url,
                "portal_name": get_site_title(),
            }

            mail_text = mail_template(**parameters)

            portal = api.portal.get()
            mail_text = portal.portal_transforms.convertTo(
                "text/mail", mail_text
            )
            sender = compose_sender(channel=self.context)

            channel_title = self.context.title
            if PY2:
                channel_title = self.context.title.encode("utf-8")

            mailHost = api.portal.get_tool(name="MailHost")
            mailHost.send(
                mail_text.getData(),
                mto=email,
                mfrom=sender,
                subject="Conferma la tua iscrizione alla Newsletter {channel}"
                " del portale {site}".format(
                    channel=channel_title, site=get_site_title()
                ),
                charset="utf-8",
                msg_type="text/html",
                immediate=True,
            )
            return data, errors

        else:
            if status == 2:
                logger.exception("user already subscribed")
                errors.append("user_already_subscribed")
                return data, errors
            else:
                logger.exception("unhandled error subscribe user")
                errors.append("Problems...{0}".format(status))
                return data, errors

    def reply(self):
        data = json_body(self.request)
        if "IDisableCSRFProtection" in dir(interfaces):
            alsoProvides(self.request, interfaces.IDisableCSRFProtection)

        _data, errors = self.handleSubscribe(data)

        return {
            "@id": self.request.get("URL"),
            "errors": errors if errors else None,
            "status": "user_subscribe_success" if not errors else "error",
        }
