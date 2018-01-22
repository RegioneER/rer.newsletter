# -*- coding: utf-8 -*-
from plone.app.layout.viewlets import ViewletBase


class ChannelManagerViewlet(ViewletBase):

    def update(self):
        pass

    def render(self):
        return self.index()
