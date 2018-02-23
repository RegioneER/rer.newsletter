# -*- coding: utf-8 -*-
from plone import api
from plone.app.layout.viewlets import ViewletBase
from zope.annotation.interfaces import IAnnotations


KEY = 'rer.newsletter.message.details'


class MessageManagerViewlet(ViewletBase):

    def update(self):
        pass

    def canManageNewsletter(self):
        if 'Editor' in api.user.get_roles() \
                or api.user.get_permissions().get(
                'rer.newsletter: Manage Newsletter'):
            return True
        else:
            return False

    def canSendMessage(self):
        if (api.content.get_state(obj=self.context) == 'review'
                and api.user.get_permissions().get(
                'rer.newsletter: Send Newsletter')) \
                or (api.content.get_state(obj=self.context) == 'review'
                    and 'Manager Newsletter' in api.user.get_roles()):
            return True
        else:
            return False

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
