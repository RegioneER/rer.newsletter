# -*- coding: utf-8 -*-
from plone import api
from plone.app.layout.viewlets import ViewletBase
from zope.annotation.interfaces import IAnnotations


KEY = 'rer.newsletter.message.details'


class MessageManagerViewlet(ViewletBase):

    def update(self):
        pass

    def canManageNewsletter(self):
        return api.user.get_permissions().get(
            'rer.newsletter: Manage Newsletter')

    def canSendMessage(self):
        return api.content.get_state(obj=self.context) == 'review'\
            and api.user.get_permissions().get(
            'rer.newsletter: Send Newsletter')

    def messageSentDetails(self):
        annotations = IAnnotations(self.context)
        if KEY in annotations.keys():
            annotations = annotations[KEY]
            messages_details = []
            for k, v in annotations.iteritems():
                messages_details.append(v)
            return messages_details
        return None

    def render(self):
        return self.index()
