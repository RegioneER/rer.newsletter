# -*- coding: utf-8 -*-
# eccezioni per mail
from smtplib import SMTPRecipientsRefused

from rer.newsletter import _
from rer.newsletter.utility.newsletter import (SUBSCRIBED, UNHANDLED,
                                               INewsletterUtility)

import premailer
from plone import api, schema
from plone.protect.authenticator import createToken
from plone.registry.interfaces import IRegistry
from plone.z3cform.layout import wrap_form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import button, field, form
from zope.component import getUtility
from zope.interface import Interface


class ISubscribeForm(Interface):
    ''' define field for newsletter subscription '''

    email = schema.Email(
        title=_(u'subscribe_user', default=u'Subscription Mail'),
        description=_(
            u'subscribe_user_description',
            default=u'Mail for subscribe to newsletter'
        ),
        required=True,
    )


class SubscribeForm(form.Form):

    ignoreContext = True
    fields = field.Fields(ISubscribeForm)

    def isVisible(self):
        if api.content.get_state(obj=self.context) == 'activated':
            return True
        else:
            return False

    @button.buttonAndHandler(u'subscribe')
    def handleSave(self, action):
        status = UNHANDLED
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        email = None
        try:

            if self.context.portal_type == 'Newsletter':
                newsletter = self.context.id_newsletter
            email = data['email']

            # controllo se la newsletter è attiva
            # se la newsletter non è attiva non faccio nemmeno vedere la form
            if not api.content.get_state(obj=self.context) == 'activated':
                raise Exception

            api_newsletter = getUtility(INewsletterUtility)
            status, secret = api_newsletter.subscribe(newsletter, email)

            if status == SUBSCRIBED:

                # creo il token CSRF
                token = createToken()

                # mando mail di conferma
                url = self.context.absolute_url()
                url += '/confirmaction?secret=' + secret
                url += '&_authenticator=' + token
                url += '&action=subscribe'

                mail_template = self.context.restrictedTraverse(
                    '@@activeuser_template'
                )

                parameters = {
                    'header': self.context.header,
                    'footer': self.context.footer,
                    'style': self.context.css_style,
                    'activationUrl': url
                }

                mail_text = mail_template(**parameters)
                mail_text = premailer.transform(mail_text)

                mailHost = api.portal.get_tool(name='MailHost')
                mailHost.send(
                    mail_text,
                    mto=email,
                    mfrom='noreply@rer.it',
                    subject='Email di attivazione',
                    charset='utf-8',
                    msg_type='text/html',
                    immediate=True
                )

                api.portal.show_message(
                    message=_(
                        u'status_user_subscribed',
                        default=u'Utente iscritto. Mail di conferma inviata.'
                    ),
                    request=self.request,
                    type=u'info'
                )

            else:
                raise Exception

        except SMTPRecipientsRefused:
            api.portal.show_message(
                message=_(
                    u'generic_problem_send_email',
                    default=u'Problem with sendind of email'
                ),
                request=self.request,
                type=u'error'
            )
        except Exception:
            # solo nel caso in cui non sia entrato nelle eccezioni precedenti
            # altrimenti vengono stampati gli errori precedenti
            if 'errors' not in self.__dict__.keys():
                self.errors = api_newsletter.getErrorMessage(status)

            api.portal.show_message(
                message=self.errors,
                request=self.request,
                type=u'error'
            )


subscribe_view = wrap_form(
    SubscribeForm,
    index=ViewPageTemplateFile('templates/subscribenewsletter.pt')
)
