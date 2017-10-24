from zope.interface import Interface
from zope import schema
from z3c.form import button, form, field
from rer.newsletter.utility.newsletter import INewsletterUtility
from rer.newsletter.utility.newsletter import OK, UNHANDLED
from zope.component import getUtility
from rer.newsletter import logger

# messaggi standard della form di dexterity
from Products.statusmessages.interfaces import IStatusMessage
from plone.dexterity.i18n import MessageFactory as dmf


def mailValidation(mail):
    # TODO
    # check if mail was valid
    return True


class IUnsubscribeForm(Interface):
    ''' define field for newsletter unsubscription '''

    mail = schema.TextLine(
        title=u"unsubscription mail",
        description=u"mail for unsubscribe from newsletter",
        required=True,
        constraint=mailValidation
    )


class UnsubscribeForm(form.Form):

    ignoreContext = True
    fields = field.Fields(IUnsubscribeForm)

    @button.buttonAndHandler(u"unsubscribe")
    def handleSave(self, action):
        status = UNHANDLED
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        # Do something with valid data here
        try:
            # TODO
            mail = ''
            newsletter = ''

            utility = getUtility(INewsletterUtility)
            status = utility.unsubscribe(self.request['form.widgets.mail'])
        except Exception:
            logger.exception(
                'unhandled error subscribing %s %s',
                newsletter,
                mail
            )
            self.errors = "Problem with subscribe"

        if status == OK:
            self.status = "Thank you very much!"
            IStatusMessage(self.request).addStatusMessage(
                dmf(self.status), "info")
            return
        else:
            if 'errors' not in self.__dict__.keys():
                self.errors = u"Ouch .... {}".format(status)

            IStatusMessage(self.request).addStatusMessage(
                dmf(self.errors), "error")
            return
