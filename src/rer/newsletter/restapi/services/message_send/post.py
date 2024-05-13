# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.services import Service
from rer.newsletter import _
from rer.newsletter.utils import OK
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides


class MessageSendPost(Service):
    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)
        res = self.context.send_message()
        status = res.get("status", "")
        if status == OK:
            return self.reply_no_content()

        msg = api.portal.translate(
            _(
                "message_send_error",
                default="Unable to send the message to subscribers. "
                "Please contact the site administrator.",
            )
        )
        self.request.response.setStatus(500)
        return dict(error=dict(type="InternalServerError", message=msg))
