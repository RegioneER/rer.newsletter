# -*- coding: utf-8 -*-
from Products.CMFPlone.resources import add_bundle_on_request
from Products.Five import BrowserView
from rer.newsletter import logger
from rer.newsletter.utility.newsletter import INewsletterUtility
from rer.newsletter.utility.newsletter import OK
from zope.component import getUtility
from zope.interface import implementer
from zope.interface import Interface

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

    def deleteUserFromNewsletter(self):

        try:
            email = self.request['email']
            newsletter = self.context.id_newsletter

            api_newsletter = getUtility(INewsletterUtility)
            status = api_newsletter.deleteUser(newsletter, email)
        except Exception:
            self.errors = api_newsletter.getMessageError(status)
            logger.exception(
                '{error}'.format(error=self.errors) +
                ' : newsletter: %s, email: %s',
                newsletter,
                email
            )

        response = {}
        if status == OK:
            response['ok'] = True
        else:
            response['ok'] = False

        return json.dumps(response)

    def exportUsersListAsFile(self):

        try:
            newsletter = self.context.id_newsletter

            api_newsletter = getUtility(INewsletterUtility)
            userList, status = api_newsletter.exportUsersList(newsletter)
        except Exception:
            self.errors = api_newsletter.getErrorMessage(status)
            logger.exception(
                '{error}'.format(error=self.errors) + ' : newsletter: %s',
                newsletter
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

        try:
            newsletter = self.context.id_newsletter

            api_newsletter = getUtility(INewsletterUtility)
            userList, status = api_newsletter.exportUsersList(newsletter)
        except Exception:
            self.errors = api_newsletter.getErrorMessage(status)
            logger.exception(
                '{error}'.format(error=self.errors) + ' : newsletter: %s',
                newsletter
            )

        if status == OK:
            return userList
