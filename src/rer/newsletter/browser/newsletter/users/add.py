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
        '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]' +
        '+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$',
        mail
    )
    if match is None:
        raise Invalid(
            _(
                u"generic_problem_email_validation",
                default=u"Una o piu delle mail inserite non sono valide"
            )
        )
    return True


class IAddForm(Interface):
    ''' define field for add user to newsletter '''

    email = schema.TextLine(
        title=_(u"add_user_admin", default=u"Add User"),
        description=_(
            u"add_user_admin_description",
            default=u"Insert email for add user to Newsletter"
        ),
        required=True,
        constraint=mailValidation
    )


class AddForm(form.Form):

    ignoreContext = True
    fields = field.Fields(IAddForm)

    @button.buttonAndHandler(_(u"add_user_admin_button", default=u"Add"))
    def handleSave(self, action):
        status = UNHANDLED
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        try:

            # TODO
            # questo valore va preso dal contesto in cui mi trovo....
            newsletter = self.context.id_newsletter
            mail = data['email']

            api_newsletter = getUtility(INewsletterUtility)
            status = api_newsletter.addUser(newsletter, mail)
        except Exception:
            logger.exception(
                'unhandled error adding %s %s',
                newsletter,
                mail
            )
            self.errors = _(
                u"generic_problem_add_user",
                default=u"Problem with add user"
            )

        if status == SUBSCRIBED:
            self.status = _(u"status_user_added", default=u"User Added")
            IStatusMessage(self.request).addStatusMessage(
                dmf(self.status), "info")
        else:
            if 'errors' not in self.__dict__.keys():
                self.errors = u"Ouch .... {}".format(status)

            IStatusMessage(self.request).addStatusMessage(
                dmf(self.errors), "error")
