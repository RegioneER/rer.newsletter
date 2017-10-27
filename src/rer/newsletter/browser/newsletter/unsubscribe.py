from zope.interface import Interface
from zope import schema
from z3c.form import button, form, field
from rer.newsletter.utility.newsletter import INewsletterUtility
from rer.newsletter.utility.newsletter import OK, UNHANDLED
from zope.component import getUtility
from rer.newsletter import logger

from rer.newsletter import newsletterMessageFactory as _

# messaggi standard della form di dexterity
from Products.statusmessages.interfaces import IStatusMessage
from plone.dexterity.i18n import MessageFactory as dmf

import re


def mailValidation(mail):
    # valido la mail
    match = re.match(
        '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$',
        mail
    )
    if match is None:
        return False

    return True


class IUnsubscribeForm(Interface):
    ''' define field for newsletter unsubscription '''

    email = schema.TextLine(
        title=_(u"unsubscribe_email_title", default=u"Unsubscription Email"),
        description=_(u"unsubscribe_email_description", default=u"Mail for unsubscribe from newsletter"),
        required=True,
        constraint=mailValidation
    )


class UnsubscribeForm(form.Form):

    ignoreContext = True
    fields = field.Fields(IUnsubscribeForm)

    @button.buttonAndHandler(_(u"unsubscribe_button", default="Unsubscribe"))
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

            # controllo se e possibile disinscriversi

            utility = getUtility(INewsletterUtility)
            status = utility.unsubscribe(newsletter, email)
        except Exception:
            logger.exception(
                'unhandled error subscribing %s %s',
                newsletter,
                email
            )
            self.errors = _(u"generic_problem_unsubscribe", default=u"Problem with unsubscribe user")

        if status == OK:
            self.status = _("user_unsubscribe_success", default=u"User unsubscribed")
            IStatusMessage(self.request).addStatusMessage(
                dmf(self.status), "info")
        else:
            if 'errors' not in self.__dict__.keys():
                self.errors = u"Ouch .... {}".format(status)

            IStatusMessage(self.request).addStatusMessage(
                dmf(self.errors), "error")
