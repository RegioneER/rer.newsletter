# -*- coding: utf-8 -*-
from Acquisition import aq_chain
from plone import api
from plone.app.layout.viewlets import ViewletBase
from plone.app.layout.viewlets.content import ContentHistoryView
from rer.newsletter.content.channel import Channel


class MessageManagerViewlet(ViewletBase):

    def render(self):
        return self.index()
