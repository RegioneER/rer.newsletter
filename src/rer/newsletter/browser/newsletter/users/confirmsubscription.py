from Products.Five.browser import BrowserView
from zope.component import getUtility
from rer.newsletter.utility.newsletter import INewsletterUtility
from rer.newsletter.utility.newsletter import OK

# messaggi standard della form di dexterity
from Products.statusmessages.interfaces import IStatusMessage
from plone.dexterity.i18n import MessageFactory as dmf

# messageFactory
from rer.newsletter import newsletterMessageFactory as _

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

        status = IStatusMessage(self.request)
        if response == OK:
            status.add(_(u"user_activated", default=u"User Activated"), type=u'info')
        else:
            status.add(u"Ouch .... {}".format(response), type=u'error')

        return self.render()
