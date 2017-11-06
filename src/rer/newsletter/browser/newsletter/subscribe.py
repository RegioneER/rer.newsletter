# -*- coding: utf-8 -*-
from plone import api
from plone import schema
from plone.protect.authenticator import createToken
from rer.newsletter import _
from rer.newsletter import logger
from rer.newsletter.utility.newsletter import INewsletterUtility
from rer.newsletter.utility.newsletter import SUBSCRIBED
from rer.newsletter.utility.newsletter import UNHANDLED
# eccezioni per mail
from smtplib import SMTPRecipientsRefused
from z3c.form import button
from z3c.form import field
from z3c.form import form
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
                raise Exception(
                    _(
                        'newsletter_not_actived',
                        default=u'Newsletter not actived'
                    )
                )

            api_newsletter = getUtility(INewsletterUtility)
            status, secret = api_newsletter.subscribe(newsletter, email)
        except Exception:
            logger.exception(
                'unhandled error subscribing %s %s',
                newsletter,
                email
            )
            self.errors = _(
                u'generic_probleme_subscribe_user',
                default=u'Problem with subscribe user'
            )

        try:
            if status == SUBSCRIBED:

                # creo il token CSRF
                token = createToken()

                # mando mail di conferma
                message = 'clicca per attivazione: '
                message += self.context.absolute_url()
                message += '/confirmsubscription_view?secret=' + secret
                message += '&_authenticator=' + token

                mailHost = api.portal.get_tool(name='MailHost')
                mailHost.send(
                    message,
                    mto=email,
                    mfrom='noreply@rer.it',
                    subject='Email di attivazione',
                    charset='utf-8',
                    msg_type='text/plain',
                    immediate=True
                    )

                api.portal.show_message(
                    message=_(
                        u'status_user_subscribed',
                        default=u'User Subscribed'
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
            if 'errors' not in self.__dict__.keys():
                self.errors = u'Ouch .... {status}'.format(status=status)

            api.portal.show_message(
                message=self.errors,
                request=self.request,
                type=u'error'
            )
