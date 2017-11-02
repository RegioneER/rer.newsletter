# -*- coding: utf-8 -*-
from plone import api
from Products.Five.browser import BrowserView


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
