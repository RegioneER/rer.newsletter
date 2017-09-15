from zope.interface import Interface
from zope import schema
from z3c.form import button, form, field
from rer.newsletter.api.mailmanhandler import MailmanHandler


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
            mh = MailmanHandler()
            mh.subscribe(self.request['form.widgets.mail'])
        except Exception:
            self.errors = "Problem with subscribe"

        # Set status on this form page
        self.status = "Thank you very much!"
