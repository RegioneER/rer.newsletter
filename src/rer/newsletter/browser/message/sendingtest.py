# -*- coding: utf-8 -*-
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
from datetime import datetime

import re


class IMessageSendingTest(Interface):
    """define field for sending test of message"""

    email = schema.Email(
        title=_(u'Email', default='Email'),
        description=_(
            u'email_sendingtest_description',
            default=u'Email to send the test message',
        ),
        required=True,
    )


class MessageSendingTest(form.Form):

    ignoreContext = True
    fields = field.Fields(IMessageSendingTest)

    def _getMessage(self, channel, message, footer):
        content = IShippable(message).message_content
        message_template = self.context.restrictedTraverse("@@messagepreview_view")
        parameters = {
            'css': channel.css_style,
            'message_header': channel.header if channel.header else u'',
            'message_footer': channel.footer if channel.footer else u'',
            'message_content': f"""
                <tr>
                    <td align="left">
                        <div class="gmail-blend-screen">
                        <div class="gmail-blend-difference">
                            <div class="divider"></div>
                        </div>
                        </div>
                        <div class="newsletterTitle">
                        <h1>{self.context.title}</h1>
                        <h4 class="newsletterDate">{
                            datetime.today().strftime('Newsletter %d %B %Y')
                        }</h4>
                    </div>

                    </td>
                </tr>
                <tr>
                    <td align="left">
                    {content}
                    </td>
                </tr>
            """,
            'message_unsubscribe_default': footer,
        }

        body = message_template(**parameters)

        # passo la mail per il transform
        portal = api.portal.get()
        body = portal.portal_transforms.convertTo("text/mail", body)

        return body

    @button.buttonAndHandler(_('send_sendingtest', default='Send'))
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        try:

            # prendo l'email dai parametri
            email = data['email']
            emails = re.compile('[,|;]').split(email)

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
                '@@unsubscribe_channel_template'
            )
            parameters = {
                'portal_name': get_site_title(),
                'channel_name': ns_obj.title,
                'unsubscribe_link': ns_obj.absolute_url(),
                "enabled": ns_obj.standard_unsubscribe,
            }
            unsubscribe_footer_text = unsubscribe_footer_template(**parameters)
            body = self._getMessage(ns_obj, message_obj, unsubscribe_footer_text)

            sender = compose_sender(channel=ns_obj)

            nl_subject = (
                ' - ' + ns_obj.subject_email if ns_obj.subject_email else u''
            )

            subject = 'Messaggio di prova - ' + message_obj.title + nl_subject
            # per mandare la mail non passo per l'utility
            # in ogni caso questa mail viene mandata da plone
            mailHost = api.portal.get_tool(name='MailHost')
            for email in emails:
                mailHost.send(
                    body.getData(),
                    mto=email.strip(),
                    mfrom=sender,
                    subject=subject,
                    charset='utf-8',
                    msg_type='text/html',
                    immediate=True,
                )

        except SMTPRecipientsRefused:
            self.errors = u'problemi con l\'invio del messaggio'

        # da sistemare la gestione degli errori
        if 'errors' in list(self.__dict__.keys()):
            api.portal.show_message(
                message=self.errors, request=self.request, type=u'error'
            )
        else:
            api.portal.show_message(
                message=u'Messaggio inviato correttamente!',
                request=self.request,
                type=u'info',
            )


message_sending_test = wrap_form(
    MessageSendingTest, index=ViewPageTemplateFile('templates/sendingtest.pt')
)
