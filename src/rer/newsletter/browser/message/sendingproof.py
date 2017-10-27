# -*- coding: utf-8 -*-
from zope.interface import Interface
from zope import schema
from z3c.form import button, form, field
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.z3cform.layout import wrap_form

from rer.newsletter import newsletterMessageFactory as _
from rer.newsletter import logger

# eccezioni per mail
from smtplib import SMTPRecipientsRefused

# api
from plone import api

# premailer
from premailer import transform

# messaggi standard della form di dexterity
from Products.statusmessages.interfaces import IStatusMessage
from plone.dexterity.i18n import MessageFactory as dmf

# Invalid
from zope.interface import Invalid

# constraint
import re


def mailValidation(mail):
    # valido la mail
    match = re.match(
        '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$',
        mail
    )
    if match is None:
        raise Invalid(_(u"generic_problem_email_validation", default=u"Una o piu delle mail inserite non sono valide"))
    return True


class IMessageSendingProof(Interface):
    ''' define field for sending proof of newsletter '''

    email = schema.TextLine(
        title=_(u"Email", default="Email"),
        description=_(u"email_sendingproof_description", default=u"Email to send the test message"),
        required=True,
        constraint=mailValidation
    )


class MessageSendingProof(form.Form):

    ignoreContext = True
    fields = field.Fields(IMessageSendingProof)

    @button.buttonAndHandler(_("send_sendingproof", default="Send"))
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
            messagePreview = ''

            messagePreview = nl.header.raw
            messagePreview += '<style> ' + nl.css_style + '</style>'
            messagePreview += self.context.text.raw
            messagePreview += nl.footer.raw

            message = transform(messagePreview)

            # risolvo tutti gli uuid
            resolveuid = re.findall('(?<=resolveuid\/)(.*?)(?=\/)', message)
            catalog = api.portal.get_tool(name='portal_catalog')
            # controllare se in questo modo viene perfetta sempre
            for uuid in resolveuid:
                res = catalog.unrestrictedSearchResults(UID=uuid)
                if res:
                    message = message.replace(
                        '../resolveuid/' + uuid, res[0].getURL()
                    )

            # per mandare la mail non passo per l'utility
            # in ogni caso questa mail viene mandata da plone
            mailHost = api.portal.get_tool(name='MailHost')
            mailHost.send(
                message,
                mto=email,
                mfrom='noreply@rer.it',
                subject='Newsletter di prova',
                charset='utf-8',
                msg_type='text/html',
                immediate=True
                )

        except SMTPRecipientsRefused:
            self.errors = u"problemi con l'invio del messaggio"
        except:
            logger.exception(
                'unhandled error for send proof of newsletter %s',
                email
            )
            self.errors = u"Problem with sending proof"

        # da sistemare la gestione degli errori
        if 'errors' in self.__dict__.keys():
            IStatusMessage(self.request).addStatusMessage(
                dmf(self.errors), "error")
        else:
            IStatusMessage(self.request).addStatusMessage(
                dmf("Messaggio inviato correttamente!"), "info")


message_sending_proof = wrap_form(
    MessageSendingProof,
    index=ViewPageTemplateFile('templates/sendingproof.pt')
)
