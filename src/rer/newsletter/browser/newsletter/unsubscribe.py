from zope.interface import Interface
from zope import schema
from z3c.form import button, form, field
from rer.newsletter.utility.newsletter import INewsletterUtility
from zope.component import getUtility


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
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        # Do something with valid data here
        try:
            mh = getUtility(INewsletterUtility)
            mh.unsubscribe(self.request['form.widgets.mail'])
        except Exception:
            self.errors = "Problem with subscribe"

        # Set status on this form page
        self.status = "Thank you very much!"
