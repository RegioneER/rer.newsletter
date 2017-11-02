# -*- coding: utf-8 -*-
from zope.component import getUtility
from zope.interface import Interface
from zope import schema
from z3c.form import button, form, field

from rer.newsletter import _
from rer.newsletter import logger
from rer.newsletter.utility.newsletter import INewsletterUtility
from rer.newsletter.utility.newsletter import SUBSCRIBED
from rer.newsletter.utility.newsletter import UNHANDLED

from plone.protect.authenticator import createToken

from plone import api

# eccezioni per mail
from smtplib import SMTPRecipientsRefused

# messaggi standard della form di dexterity
from Products.statusmessages.interfaces import IStatusMessage

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


class ISubscribeForm(Interface):
    ''' define field for newsletter subscription '''

    email = schema.TextLine(
        title=_(u"subscribe_user", default=u"Subscription Mail"),
        description=_(u"subscribe_user_description", default=u"Mail for subscribe to newsletter"),
        required=True,
        constraint=mailValidation
    )


class SubscribeForm(form.Form):

    ignoreContext = True
    fields = field.Fields(ISubscribeForm)

    @button.buttonAndHandler(u"subscribe")
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
                raise Exception(_("newsletter_not_actived", default=u"Newsletter not actived"))

            api_newsletter = getUtility(INewsletterUtility)
            status, secret = api_newsletter.subscribe(newsletter, email)
        except:
            logger.exception(
                'unhandled error subscribing %s %s',
                newsletter,
                email
            )
            self.errors = _(u"generic_probleme_subscribe_user", default=u"Problem with subscribe user")

        response = IStatusMessage(self.request)
        try:
            if status == SUBSCRIBED:

                # creo il token CSRF
                token = createToken()

                # mando mail di conferma
                message = "clicca per attivazione: " + self.context.absolute_url() + '/confirmsubscription_view?secret=' + secret + '&_authenticator=' + token

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

                response.add(_(u"status_user_subscribed", default=u"User Subscribed"), type=u'info')

            else:
                raise Exception

        except SMTPRecipientsRefused:
            response.add(_(u"generic_problem_send_email", default=u"Problem with sendind of email"), type=u'error')
        except:
            if 'errors' not in self.__dict__.keys():
                self.errors = u"Ouch .... {}".format(status)

            response.add(self.errors, type=u'error')
