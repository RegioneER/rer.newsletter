# -*- coding: utf-8 -*-
from plone import api
from plone import schema
from plone.z3cform.layout import wrap_form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from rer.newsletter import _
from rer.newsletter import logger
from rer.newsletter.utility.newsletter import INewsletterUtility
from rer.newsletter.utility.newsletter import OK
from rer.newsletter.utility.newsletter import UNHANDLED
from z3c.form import button
from z3c.form import field
from z3c.form import form
from zope.component import getUtility
from zope.interface import Interface


class IUnsubscribeForm(Interface):
    ''' define field for newsletter unsubscription '''

    email = schema.Email(
        title=_(u'unsubscribe_email_title', default=u'Unsubscription Email'),
        description=_(
            u'unsubscribe_email_description',
            default=u'Mail for unsubscribe from newsletter'
        ),
        required=True,
    )


class UnsubscribeForm(form.Form):

    ignoreContext = True
    fields = field.Fields(IUnsubscribeForm)

    def isVisible(self):
        if api.content.get_state(obj=self.context) == 'activated':
            return True
        else:
            return False

    @button.buttonAndHandler(_(u'unsubscribe_button', default='Unsubscribe'))
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

            api_newsletter = getUtility(INewsletterUtility)
            status = api_newsletter.unsubscribe(newsletter, email)
        except Exception:
            logger.exception(
                'unhandled error subscribing %s %s',
                newsletter,
                email
            )
            api.portal.show_message(
                message=_(
                    u'generic_problem_unsubscribe',
                    default=u'Problem with unsubscribe user'
                ),
                request=self.request,
                type=u'error'
            )

        if status == OK:
            api.portal.show_message(
                message=_(
                    u'user_unsubscribe_success',
                    default=u'User unsubscribed'
                ),
                request=self.request,
                type=u'info'
            )
        else:
            if 'errors' not in self.__dict__.keys():
                self.errors = api_newsletter.getErrorMessage(status)
            api.portal.show_message(
                message=self.errors,
                request=self.request,
                type=u'error'
            )


unsubscribe_view = wrap_form(
    UnsubscribeForm,
    index=ViewPageTemplateFile('templates/subscribenewsletter.pt')
)
