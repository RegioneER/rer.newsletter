# -*- coding: utf-8 -*-
from zope.component import getUtility
from zope.interface import Interface
from zope import schema
from z3c.form import button, form, field

from rer.newsletter import newsletterMessageFactory as _
from rer.newsletter import logger
from rer.newsletter.utility.newsletter import INewsletterUtility
from rer.newsletter.utility.newsletter import SUBSCRIBED
from rer.newsletter.utility.newsletter import UNHANDLED

from plone import api

# messaggi standard della form di dexterity
from Products.statusmessages.interfaces import IStatusMessage
from plone.dexterity.i18n import MessageFactory as dmf


def mailValidation(mail):
    # TODO
    # check if mail was valid
    return True


class ISubscribeForm(Interface):
    ''' define field for newsletter subscription '''

    mail = schema.TextLine(
        title=u"subscription mail",
        description=u"mail for subscribe to newsletter",
        required=True,
        constraint=mailValidation
    )


class SubscribeForm(form.Form):

    ignoreContext = True
    fields = field.Fields(ISubscribeForm)

    @button.buttonAndHandler(u"subscribe")
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        try:

            # TODO
            newsletter = u'newsletter@example.org'
            mail = data['mail']

            # controllo se la newsletter è attiva
            # se la newsletter non è attiva non faccio nemmeno vedere la form
            if not api.content.get_state(obj=self.context) == 'activated':
                raise Exception('Newsletter not activated')

            api_newsletter = getUtility(INewsletterUtility)
            status = api_newsletter.subscribe(newsletter, mail)
        except:
            logger.exception(
                'unhandled error subscribing %s %s',
                newsletter,
                mail
            )
            self.errors = u"Problem with subscribe"

        if status == SUBSCRIBED:
            self.status = u"Thank you very much!"
            IStatusMessage(self.request).addStatusMessage(
                dmf(self.status), "info")
            return
        else:
            self.status = u"Ouch .... {}".format(status)
            IStatusMessage(self.request).addStatusMessage(
                dmf(self.errors + ' status: ' + self.status), "error")
            return
