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
        # Do something with valid data here
        try:
            mail = data['mail']
            newsletter = u'newsletter@example.org'  # TODO
            api = getUtility(INewsletterUtility)
            status = api.subscribe(newsletter, mail)
        except:
            logger.exception('unhandled error subscribing %s %s', newsletter, mail)
            self.errors = u"Problem with subscribe"
            status = UNHANDLED

        if status == SUBSCRIBED:
            self.status = u"Thank you very much!"
        else:
            self.status = u"Ouch .... {}".format(status)
