# -*- coding: utf-8 -*-
from plone import api
from plone import schema
from plone.dexterity.i18n import MessageFactory as dmf
from plone.z3cform.layout import wrap_form
from premailer import transform
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from rer.newsletter import _
# from rer.newsletter import logger
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


# FIXME: qui c'è del codice completamente ripetuto rispetto a utility/base
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

            if self.context.portal_type == 'Newsletter':
                nl = self.context.id_newsletter
            email = data['email']

            # monto la newsletter da mandare
            nl = self.context.aq_parent
            body = u''
            body += nl.header.raw if nl.header else u''
            body += '<style>{css}</style>'.format(css=nl.css_style or u'')
            body += self.context.text.output if self.context.text else u''
            body += nl.footer.output if nl.footer else u''
            body = transform(body)

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
        # except Exception:
        #     logger.exception(
        #         'unhandled error for send proof of newsletter %s',
        #         email
        #     )
        #     self.errors = u'Problem with sending proof'

        # TODO: da sistemare la gestione degli errori
        if 'errors' in self.__dict__.keys():
            IStatusMessage(self.request).addStatusMessage(
                dmf(self.errors), 'error')
        else:
            IStatusMessage(self.request).addStatusMessage(
                dmf('Messaggio inviato correttamente!'), 'info')


message_sending_proof = wrap_form(
    MessageSendingProof,
    index=ViewPageTemplateFile('templates/sendingproof.pt')
)
