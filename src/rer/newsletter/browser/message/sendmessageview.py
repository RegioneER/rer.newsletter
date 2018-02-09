# -*- coding: utf-8 -*-
from datetime import datetime
from persistent.dict import PersistentDict
from plone import api
from plone.z3cform.layout import wrap_form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from rer.newsletter import _
from rer.newsletter import logger
from rer.newsletter.content.channel import Channel
from rer.newsletter.utility.channel import IChannelUtility
from rer.newsletter.utility.channel import OK
from z3c.form import button
from z3c.form import form
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility


KEY = 'rer.newsletter.message.details'


class SendMessageView(form.Form):

    ignoreContext = True

    def _getNewsletter(self):
        channel = None
        for obj in self.context.aq_chain:
            if isinstance(obj, Channel):
                channel = obj
                break
        else:
            if not channel:
                return
        return channel

    def getUserNumber(self):
        channel = self._getNewsletter()

        api_channel = getUtility(IChannelUtility)
        active_users, status = api_channel.getNumActiveSubscribers(
            channel.id_channel
        )
        if status == OK:
            return active_users
        else:
            return 0

    @button.buttonAndHandler(_('send_sendingview', default='Send'))
    def handleSave(self, action):
        channel = self._getNewsletter()

        api_channel = getUtility(IChannelUtility)
        api_channel.sendMessage(
            channel.id_channel, self.context
        )

        # i dettagli sull'invio del messaggio per lo storico
        annotations = IAnnotations(self.context)
        if KEY not in annotations.keys():
            active_users, status = api_channel.getNumActiveSubscribers(
                channel.id_channel
            )

            if status != OK:
                logger.exception(
                    'Problems...{0}'.format(status),
                )

            annotations[KEY] = PersistentDict({
                'num_active_subscribers': active_users,
                'send_date': datetime.today().strftime(
                    '%d/%m/%Y %H:%M:%S'
                ),
            })

        # transition
        api.content.transition(obj=self.context, transition='send')

        self.request.response.redirect('view')
        api.portal.show_message(
            message=_(u'message_send', default='Message send'),
            request=self.request,
            type=u'info'
        )


message_sending_view = wrap_form(
    SendMessageView,
    index=ViewPageTemplateFile('templates/sendmessageview.pt')
)
