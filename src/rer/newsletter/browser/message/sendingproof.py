# -*- coding: utf-8 -*-
from plone import api
from plone import schema
from plone.z3cform.layout import wrap_form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from rer.newsletter import _
from rer.newsletter.utility.newsletter import INewsletterUtility
# from rer.newsletter import logger
from smtplib import SMTPRecipientsRefused
from z3c.form import button
from z3c.form import field
from z3c.form import form
from zope.component import getUtility
from zope.interface import Interface


class IMessageSendingProof(Interface):
    ''' define field for sending proof of newsletter '''

    email = schema.Email(
        title=_(u'Email', default='Email'),
        description=_(
            u'email_sendingproof_description',
            default=u'Email to send the test message'
        ),
        required=True,
    )


class MessageSendingProof(form.Form):

    ignoreContext = True
    fields = field.Fields(IMessageSendingProof)

    @button.buttonAndHandler(_('send_sendingproof', default='Send'))
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        try:

            # prendo l'email dai parametri
            email = data['email']

            # monto la newsletter da mandare
            utility = getUtility(INewsletterUtility)
            body = utility.getMessage(self.context.aq_parent, self.context)

            # per mandare la mail non passo per l'utility
            # in ogni caso questa mail viene mandata da plone
            mailHost = api.portal.get_tool(name='MailHost')
            mailHost.send(
                body,
                mto=email,
                mfrom='noreply@rer.it',
                subject='Newsletter di prova',
                charset='utf-8',
                msg_type='text/html',
                immediate=True
                )

        except SMTPRecipientsRefused:
            self.errors = u'problemi con l\'invio del messaggio'

        # da sistemare la gestione degli errori
        if 'errors' in self.__dict__.keys():
            api.portal.show_message(
                message=self.errors,
                request=self.request,
                type=u'error'
            )
        else:
            api.portal.show_message(
                message=u'Messaggio inviato correttamente!',
                request=self.request,
                type=u'info'
            )


message_sending_proof = wrap_form(
    MessageSendingProof,
    index=ViewPageTemplateFile('templates/sendingproof.pt')
)
