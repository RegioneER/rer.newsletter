# -*- coding: utf-8 -*-
from plone import api
from Products.Five.browser import BrowserView
from rer.newsletter.utility.newsletter import INewsletterUtility
from rer.newsletter.utility.newsletter import OK
from zope.component import getUtility


# disable CSRF
# from plone.protect.interfaces import IDisableCSRFProtection
# from zope.interface import alsoProvides


class ConfirmSubscription(BrowserView):

    def render(self):
        return self.index()

    def __call__(self):
        # alsoProvides(self.request, IDisableCSRFProtection)
        secret = self.request.get('secret')

        response = None
        if self.context.portal_type == 'Newsletter':
            api_newsletter = getUtility(INewsletterUtility)
            response = api_newsletter.activeUser(
                self.context.id_newsletter,
                secret
            )

        if response == OK:
            api.portal.show_message(
                message=api_newsletter.getErrorMessage(response),
                request=self.request,
                type=u'info'
            )
        else:
            api.portal.show_message(
                message=api_newsletter.getErrorMessage(response),
                request=self.request,
                type=u'error'
            )

        return self.render()
