# -*- coding: utf-8 -*-
from rer.newsletter.utility.newsletter import OK, INewsletterUtility

from plone import api
from Products.Five.browser import BrowserView
from zope.component import getUtility

# disable CSRF
# from plone.protect.interfaces import IDisableCSRFProtection
# from zope.interface import alsoProvides


class ConfirmAction(BrowserView):

    def render(self):
        return self.index()

    def __call__(self):
        secret = self.request.get('secret')
        action = self.request.get('action')

        response = None
        api_newsletter = getUtility(INewsletterUtility)

        if action == u'subscribe':
            response = api_newsletter.activeUser(
                self.context.id_newsletter,
                secret=secret
            )
        elif action == u'unsubscribe':
            response = api_newsletter.deleteUser(
                self.context.id_newsletter,
                secret=secret
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
