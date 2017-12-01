# -*- coding: utf-8 -*-
# from rer.newsletter import logger
from plone import api
from plone import schema
from plone.z3cform.layout import wrap_form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from rer.newsletter import _
from smtplib import SMTPRecipientsRefused
from z3c.form import button
from z3c.form import field
from z3c.form import form
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
            ns_obj = self.context.aq_parent
            message_obj = self.context

            body = u''
            body += ns_obj.header.output if ns_obj.header else u''
            body += u'<style>{css}</style>'.format(
                css=ns_obj.css_style or u''
            )
            body += message_obj.text.output if message_obj.text else u''
            body += ns_obj.footer.output if ns_obj.footer else u''

            # passo la mail per il transform
            portal = api.portal.get()
            body = portal.portal_transforms.convertTo('text/mail', body)

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
