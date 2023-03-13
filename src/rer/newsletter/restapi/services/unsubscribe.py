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
from rer.newsletter.utils import OK
from rer.newsletter.utils import UNHANDLED
from six import PY2
from zope.component import getMultiAdapter
from zope.interface import alsoProvides


class NewsletterUnsubscribe(Service):
    def reply(self):
        data = json_body(self.request)
        if "IDisableCSRFProtection" in dir(interfaces):
            alsoProvides(self.request, interfaces.IDisableCSRFProtection)
        response, errors = self.handleUnsubscribe(data)
        if errors:
            response["errors"] = errors
        return response

    def getData(self, data):
        errors = []
        if not data.get("email", None):
            errors.append("Indirizzo email non inserito o non valido")
        return {
            "email": data.get("email", None),
        }, errors

    def handleUnsubscribe(self, postData):
        status = UNHANDLED
        data, errors = self.getData(postData)
        if errors:
            return data, errors

        email = data.get("email", None)

        channel = getMultiAdapter(
            (self.context, self.request), IChannelSubscriptions
        )

        status, secret = channel.unsubscribe(email)

        if status != OK:
            logger.exception("Error: {}".format(status))
            if status == 4:
                msg = "unsubscribe_inexistent_mail"

            else:
                msg = "unsubscribe_generic"
            errors = msg
            return {"@id": self.request.get("URL")}, errors

        # creo il token CSRF
        token = createToken()

        # mando mail di conferma
        url = self.context.absolute_url()
        url += "/confirm-subscription?secret=" + secret
        url += "&_authenticator=" + token
        url += "&action=unsubscribe"

        mail_template = self.context.restrictedTraverse(
            "@@deleteuser_template"
        )

        parameters = {
            "header": self.context.header,
            "footer": self.context.footer,
            "style": self.context.css_style,
            "activationUrl": url,
        }

        mail_text = mail_template(**parameters)

        portal = api.portal.get()
        mail_text = portal.portal_transforms.convertTo("text/mail", mail_text)

        response_email = compose_sender(channel=self.context)
        channel_title = self.context.title
        if PY2:
            channel_title = self.context.title.encode("utf-8")

        mailHost = api.portal.get_tool(name="MailHost")
        mailHost.send(
            mail_text.getData(),
            mto=email,
            mfrom=response_email,
            subject="Conferma la cancellazione dalla newsletter"
            " {channel} del portale {site}".format(
                channel=channel_title, site=get_site_title()
            ),
            charset="utf-8",
            msg_type="text/html",
            immediate=True,
        )

        return {
            "@id": self.request.get("URL"),
            "status": "user_unsubscribe_success" if not errors else "error",
            "errors": errors if errors else None,
        }, errors
