# -*- coding: utf-8 -*-
from plone import api
from Products.CMFPlone.resources import add_bundle_on_request
from Products.Five.browser import BrowserView
from zope.annotation.interfaces import IAnnotations

import json


KEY = 'rer.newsletter.channel.history'


class ChannelHistory(BrowserView):
    def __init__(self, context, request):
        self.context = context
        self.request = request

        add_bundle_on_request(self.request, 'message_datatables')

    def getMessageSentDetails(self):

        annotations = IAnnotations(self.context)
        history = [x.data for x in annotations.get(KEY, [])]
        return json.dumps(history[::-1])

    def deleteMessageFromHistory(self):
        message_history = self.request.get('message_history')

        # recupero tutti i messaggi del canale
        messages = api.content.find(
            context=self.context, portal_type='Message'
        )
        for message in messages:
            obj = message.getObject()
            annotations = IAnnotations(obj)
            if KEY in list(annotations.keys()):
                annotations = annotations[KEY]
                for k in annotations.keys():
                    if message_history == k:
                        del annotations[k]
                        break
        response = {}
        response['ok'] = True
        return json.dumps(response)
