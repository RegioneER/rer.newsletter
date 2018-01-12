# -*- coding: utf-8 -*-
from Products.CMFPlone.resources import add_bundle_on_request
from Products.Five import BrowserView
from rer.newsletter import logger
from rer.newsletter.utility.channel import IChannelUtility, OK, UNHANDLED
from zope.component import getUtility
from zope.interface import Interface, implementer

import csv
import json
import StringIO


class IManageUsers(Interface):
    pass


@implementer(IManageUsers)
class ManageUsers(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

        add_bundle_on_request(self.request, 'datatables')

    def deleteUser(self):

        status = UNHANDLED
        try:
            email = self.request['email']
            channel = self.context.id_channel

            api_channel = getUtility(IChannelUtility)
            status = api_channel.deleteUser(channel, email)
        except Exception:
            self.errors = api_channel.getMessageError(status)
            logger.exception(
                '{error}'.format(error=self.errors) +
                ' : channel: %s, email: %s',
                channel,
                email
            )

        response = {}
        if status == OK:
            response['ok'] = True
        else:
            response['ok'] = False

        return json.dumps(response)

    def exportUsersListAsFile(self):

        status = UNHANDLED
        try:
            channel = self.context.id_channel

            api_channel = getUtility(IChannelUtility)
            userList, status = api_channel.exportUsersList(channel)
        except Exception:
            self.errors = api_channel.getErrorMessage(status)
            logger.exception(
                '{error}'.format(error=self.errors) + ' : channel: %s',
                channel
            )

        if status == OK:
            # predisporre download del file
            data = StringIO.StringIO()
            fieldnames = ['id', 'email', 'is_active', 'creation_date']
            writer = csv.DictWriter(data, fieldnames=fieldnames)

            writer.writeheader()

            userListJson = json.loads(userList)
            for user in userListJson:
                writer.writerow(user)

            filename = '{title}-user-list.csv'.format(title=self.context.title)

            self.request.response.setHeader('Content-Type', 'text/csv')
            self.request.response.setHeader(
                'Content-Disposition',
                'attachment; filename="{filename}"'.format(filename=filename)
            )

            return data.getvalue()

    def exportUsersListAsJson(self):

        status = UNHANDLED
        try:
            channel = self.context.id_channel

            api_channel = getUtility(IChannelUtility)
            userList, status = api_channel.exportUsersList(channel)
        except Exception:
            self.errors = api_channel.getErrorMessage(status)
            logger.exception(
                '{error}'.format(error=self.errors) + ' : channel: %s',
                channel
            )

        if status == OK:
            return userList
