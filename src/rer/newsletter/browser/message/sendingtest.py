# -*- coding: utf-8 -*-
from datetime import datetime
from plone import api
from plone import schema
from plone.z3cform.layout import wrap_form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from rer.newsletter import _
from rer.newsletter.behaviors.ships import IShippable
from rer.newsletter.content.channel import Channel
from rer.newsletter.utils import compose_sender
from rer.newsletter.utils import get_site_title
from smtplib import SMTPRecipientsRefused
from z3c.form import button
from z3c.form import field
from z3c.form import form
from zope.interface import Interface

import re


class IMessageSendingTest(Interface):
    """define field for sending test of message"""

    email = schema.Email(
        title=_("Email", default="Email"),
        description=_(
            "email_sendingtest_description",
            default="Email to send the test message",
        ),
        required=True,
    )


class MessageSendingTest(form.Form):
    ignoreContext = True
    fields = field.Fields(IMessageSendingTest)

    def _getDate(self):
        # this would be good but it doesn't work, locale not supported
        # try:
        #     locale.setlocale(locale.LC_ALL, 'it_IT.utf8')
        # except Exception:
        #     try:
        #         locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')
        #     except Exception:
        #         locale.setlocale(locale.LC_ALL, 'it_IT')
        return datetime.today().strftime("Newsletter %d-%m-%Y")

    def _getMessage(self, channel, message, footer):
        content = IShippable(message).message_content
        message_template = self.context.restrictedTraverse(
            "@@messagepreview_view"
        )
        parameters = {
            "css": channel.css_style,
            "message_header": channel.header if channel.header else "",
            "message_subheader": f"""
                <tr>
                    <td align="left" colspan="2">
                      <div class="newsletterTitle">
                        <h1>{self.context.title}</h1>
                      </div>
                    </td>
                </tr>""",
            "message_footer": channel.footer if channel.footer else "",
            "message_content": f"""
                <tr>
                    <td align="left" colspan="2">
                    {content}
                    </td>
                </tr>
            """,
            "message_unsubscribe_default": footer,
        }

        body = message_template(**parameters)

        # passo la mail per il transform
        portal = api.portal.get()
        body = portal.portal_transforms.convertTo("text/mail", body)

        return body

    @button.buttonAndHandler(_("send_sendingtest", default="Send"))
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        try:
            # prendo l'email dai parametri
            email = data["email"]
            emails = re.compile("[,|;]").split(email)

            ns_obj = None
            for obj in self.context.aq_chain:
                if isinstance(obj, Channel):
                    ns_obj = obj
                    break
            else:
                if not ns_obj:
                    # non riesco a recuperare le info di un channel
                    return
            message_obj = self.context

            unsubscribe_footer_template = self.context.restrictedTraverse(
                "@@unsubscribe_channel_template"
            )
            parameters = {
                "portal_name": get_site_title(),
                "channel_name": ns_obj.title,
                "unsubscribe_link": ns_obj.absolute_url(),
                "enabled": ns_obj.standard_unsubscribe,
            }
            unsubscribe_footer_text = unsubscribe_footer_template(**parameters)
            body = self._getMessage(
                ns_obj, message_obj, unsubscribe_footer_text
            )

            sender = compose_sender(channel=ns_obj)

            nl_subject = (
                " - " + ns_obj.subject_email if ns_obj.subject_email else ""
            )

            subject = "Messaggio di prova - " + message_obj.title + nl_subject
            # per mandare la mail non passo per l'utility
            # in ogni caso questa mail viene mandata da plone
            mailHost = api.portal.get_tool(name="MailHost")
            for email in emails:
                mailHost.send(
                    body.getData(),
                    mto=email.strip(),
                    mfrom=sender,
                    subject=subject,
                    charset="utf-8",
                    msg_type="text/html",
                    immediate=True,
                )

        except SMTPRecipientsRefused:
            self.errors = "problemi con l'invio del messaggio"

        # da sistemare la gestione degli errori
        if "errors" in list(self.__dict__.keys()):
            api.portal.show_message(
                message=self.errors, request=self.request, type="error"
            )
        else:
            api.portal.show_message(
                message="Messaggio inviato correttamente!",
                request=self.request,
                type="info",
            )


message_sending_test = wrap_form(
    MessageSendingTest, index=ViewPageTemplateFile("templates/sendingtest.pt")
)
