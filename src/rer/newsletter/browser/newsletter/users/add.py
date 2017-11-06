# -*- coding: utf-8 -*-
from plone import api
from plone import schema
from rer.newsletter import _
from rer.newsletter import logger
from rer.newsletter.utility.newsletter import INewsletterUtility
from rer.newsletter.utility.newsletter import SUBSCRIBED
from rer.newsletter.utility.newsletter import UNHANDLED
from z3c.form import button
from z3c.form import field
from z3c.form import form
from zope.component import getUtility
from zope.interface import Interface


class IAddForm(Interface):
    ''' define field for add user to newsletter '''

    email = schema.Email(
        title=_(u'add_user_admin', default=u'Add User'),
        description=_(
            u'add_user_admin_description',
            default=u'Insert email for add user to Newsletter'
        ),
        required=True,
    )


class AddForm(form.Form):

    ignoreContext = True
    fields = field.Fields(IAddForm)

    @button.buttonAndHandler(_(u'add_user_admin_button', default=u'Add'))
    def handleSave(self, action):
        status = UNHANDLED
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        try:

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
                u'generic_problem_add_user',
                default=u'Problem with add user'
            )

        if status == SUBSCRIBED:
            status = _(u'status_user_added', default=u'User Added')
            api.portal.show_message(
                message=status,
                request=self.request,
                type=u'info'
            )

        else:
            if 'errors' not in self.__dict__.keys():
                self.errors = u'Ouch .... {status}'.format(status=status)

            api.portal.show_message(
                message=self.errors,
                request=self.request,
                type=u'error'
            )
