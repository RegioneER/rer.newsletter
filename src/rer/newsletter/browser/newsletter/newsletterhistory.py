# -*- coding: utf-8 -*-
from plone import api
from Products.CMFPlone.resources import add_bundle_on_request
from Products.Five.browser import BrowserView
from zope.annotation.interfaces import IAnnotations

import json
KEY = 'rer.newsletter.message.details'


class NewsletterHistory(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

        add_bundle_on_request(self.request, 'message_datatables')

    def getMessageSentDetails(self):

        if self.context.portal_type == 'Newsletter':
            messageList = api.content.find(
                context=self.context,
                portal_type='Message'
            )

        activeMessageList = []
        count = 0
        if messageList:
            for message in messageList:
                obj = message.getObject()
                if api.content.get_state(obj=obj) == 'sent':
                    annotations = IAnnotations(obj)
                    if KEY in annotations.keys():
                        au = annotations[KEY]['num_active_subscribers']
                        sd = annotations[KEY]['send_date']

                        element = {}
                        element['id'] = count
                        element['message'] = obj.title
                        element['active_users'] = au
                        element['send_date'] = sd
                        count += 1
                        activeMessageList.append(element)

        return json.dumps(activeMessageList)
