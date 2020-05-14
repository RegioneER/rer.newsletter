# -*- coding: utf-8 -*-
from Acquisition import aq_chain
from plone import api
from plone.app.layout.viewlets import ViewletBase
from plone.app.layout.viewlets.content import ContentHistoryView
from rer.newsletter.content.channel import Channel


class MessageManagerViewlet(ViewletBase):
    def _getChannel(self):
        return [x for x in aq_chain(self.context) if isinstance(x, Channel)]

    def canManageNewsletter(self):

        if not self._getChannel():
            return False

        isEditor = 'Editor' in api.user.get_roles(obj=self.context)
        hasManageNewsletter = api.user.get_permissions(obj=self.context).get(
            'rer.newsletter: Manage Newsletter'
        ) and 'Gestore Newsletter' not in api.user.get_roles(obj=self.context)
        if isEditor or hasManageNewsletter:
            return True
        else:
            return False

    def canSendMessage(self):

        if not self._getChannel():
            return False

        if api.content.get_state(
            obj=self.context
        ) == 'published' and api.user.get_permissions(obj=self.context).get(
            'rer.newsletter: Send Newsletter'
        ):
            return True
        else:
            return False

    def messageAlreadySent(self):
        history = ContentHistoryView(self.context, self.request).fullHistory()
        if not history:
            return False
        send_history = [x for x in history if x['action'] == 'Invio']
        return len(send_history) > 0

    def render(self):
        return self.index()
