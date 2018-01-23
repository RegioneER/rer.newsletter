# -*- coding: utf-8 -*-
from plone import api
from plone.app.layout.viewlets import ViewletBase


class MessageManagerViewlet(ViewletBase):

    def update(self):
        pass

    def render(self):
        return self.index()


class MessageSendViewlet(ViewletBase):

    def update(self):
        pass

    def getState(self):
        return api.content.get_state(obj=self.context)

    def render(self):
        return self.index()
