# -*- coding: utf-8 -*-
from plone import api
from Products.Five.browser import BrowserView


class NewsletterView(BrowserView):

    def getState(self, state):
        stateDict = {
            "draft": "bozza",
            "review": "in attesa di invio",
            "sent": "inviato"
        }

        return stateDict[state]

    def getMessageList(self):

        if self.context.portal_type == 'Newsletter':
            messageList = api.content.find(
                context=self.context,
                portal_type='Message'
            )

            ml = []
            for message in messageList:
                message_obj = message.getObject()

                setattr(message_obj, 'state', self.getState(
                    api.content.get_state(obj=message_obj)
                ))

                ml.append(message_obj)

            return ml
