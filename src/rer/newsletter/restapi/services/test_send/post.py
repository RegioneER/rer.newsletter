# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zExceptions import BadRequest
from rer.newsletter import _


class TestSendPost(Service):
    def reply(self):
        data = json_body(self.request)

        email = data.get("email", "")
        if not email:
            raise BadRequest(
                api.portal.translate(
                    _(
                        "test_send_missing_email",
                        default="Missing required parameter: email.",
                    )
                )
            )

        self.context.send_preview(email=email)

        return self.reply_no_content()
