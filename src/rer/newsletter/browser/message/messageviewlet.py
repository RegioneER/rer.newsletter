# -*- coding: utf-8 -*-
from plone import api
from plone.app.layout.viewlets import ViewletBase


class MessageManagerViewlet(ViewletBase):

    def update(self):
        pass

    def isVisible(self):
        return api.content.get_state(obj=self.context) == 'review'\
            and api.user.get_permissions().get(
            'rer.newsletter: Send Newsletter')

    def render(self):
        return self.index()
