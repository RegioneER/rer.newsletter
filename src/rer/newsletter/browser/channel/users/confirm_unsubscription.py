# -*- coding: utf-8 -*-
from plone import api
from Products.Five.browser import BrowserView
from rer.newsletter import _
from rer.newsletter.adapter.subscriptions import IChannelSubscriptions
from rer.newsletter.contentrules.events import UnsubscriptionEvent
from rer.newsletter.utils import OK
from zope.component import getMultiAdapter
from zope.event import notify

import logging

logger = logging.getLogger(__name__)


class ConfirmUnsubscription(BrowserView):

    def __call__(self):
        secret = self.request.get("secret")

        response = None
        channel = getMultiAdapter(
            (self.context, self.request), IChannelSubscriptions
        )

        secret = self.request.form.get('secret', "")
        submitted = self.request.form.get('submitted', "")

        if not secret:
            api.portal.show_message(
                message=_(
                    u"unsubscribe_missing_secret",
                    default=u"Unable to unsubscribe to channel. Missing secret key.",
                ), request=self.request, type=u"error",
            )
            return self.request.response.redirect(self.context.absolute_url())
        if not submitted or self.request.method != 'POST':
            return super(ConfirmUnsubscription, self).__call__()

        response, mail = channel.deleteUserWithSecret(secret=secret)
        if response == OK:
            notify(UnsubscriptionEvent(self.context, mail))
            api.portal.show_message(
                message=_(u"generic_delete_message_success",default=u"Succesfully unsubscribed."), request=self.request, type=u"info",
            )
        else:
            logger.error(
                'Unable to unsubscribe user with token "{token}" on channel {channel}.'.format(  # noqa
                    token=secret, channel=self.context.absolute_url()
                )
            )
            api.portal.show_message(
                message=_(
                    "unable_to_unsubscribe",
                    default=u"Unable to unsubscribe to this channel."
                    u" Please contact site administrator.",
                ),
                request=self.request,
                type=u"error",
            )

        return self.request.response.redirect(self.context.absolute_url())
