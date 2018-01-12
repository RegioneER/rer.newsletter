# -*- coding: utf-8 -*-
from smtplib import SMTPRecipientsRefused

from rer.newsletter.utility.channel import (OK, PROBLEM_WITH_MAIL,
                                            IChannelUtility)

from plone import api
from Products.Five.browser import BrowserView
from zope.component import getUtility

# disable CSRF
# from plone.protect.interfaces import IDisableCSRFProtection
# from zope.interface import alsoProvides


class ConfirmAction(BrowserView):

    def render(self):
        return self.index()

    def _sendGenericMessage(self, template, receiver, message, message_title):
        try:
            mail_template = self.context.restrictedTraverse(
                '@@{0}'.format(template)
            )

            parameters = {
                'header': self.context.header,
                'footer': self.context.footer,
                'style': self.context.css_style
            }

            mail_text = mail_template(**parameters)

            portal = api.portal.get()
            mail_text = portal.portal_transforms.convertTo(
                'text/mail', mail_text)

            # invio la mail ad ogni utente
            mail_host = api.portal.get_tool(name='MailHost')
            mail_host.send(
                mail_text.getData(),
                mto=receiver,
                mfrom="noreply@rer.it",
                subject=message_title,
                charset='utf-8',
                msg_type='text/html'
            )
        except SMTPRecipientsRefused:
            raise SMTPRecipientsRefused
        except Exception:
            # da gestire
            raise Exception

        return OK

    def __call__(self):
        secret = self.request.get('secret')
        action = self.request.get('action')

        response = None
        api_channel = getUtility(IChannelUtility)

        if action == u'subscribe':
            response, user = api_channel.activeUser(
                self.context.id_channel,
                secret=secret
            )
            # mandare mail di avvenuta conferma
            if response == OK:
                try:
                    self._sendGenericMessage(
                        template='activeuserconfirm_template',
                        receiver=user,
                        message='Messaggio di avvenuta iscrizione',
                        message_title='Iscrizione confermata'
                    )
                except SMTPRecipientsRefused:
                    response = PROBLEM_WITH_MAIL

        elif action == u'unsubscribe':
            response, user = api_channel.deleteUser(
                self.context.id_channel,
                secret=secret
            )
            # mandare mail di avvenuta cancellazione
            if response == OK:
                try:
                    self._sendGenericMessage(
                        template='deleteuserconfirm_template',
                        receiver=user,
                        message='L\'utente è stato eliminato dalla channel',
                        message_title='Cancellazione avvenuta'
                    )
                except SMTPRecipientsRefused:
                    response = PROBLEM_WITH_MAIL

        if response == OK:
            api.portal.show_message(
                message=api_channel.getErrorMessage(response),
                request=self.request,
                type=u'info'
            )
        else:
            api.portal.show_message(
                message=api_channel.getErrorMessage(response),
                request=self.request,
                type=u'error'
            )

        return self.render()
