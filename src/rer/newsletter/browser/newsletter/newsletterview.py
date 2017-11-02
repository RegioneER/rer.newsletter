# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from plone import api


class NewsletterView(BrowserView):

    def getMessageList(self):

        if self.context.portal_type == 'Newsletter':
            messageList = api.content.find(
                context=self.context,
                portal_type='Message'
            )

            ml = []
            for message in messageList:
                ml.append(message.getObject())

            return ml
