# -*- coding: utf-8 -*-
from plone.dexterity.i18n import MessageFactory as dmf
from Products.CMFPlone.resources import add_bundle_on_request
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from rer.newsletter import _
from rer.newsletter import logger
from rer.newsletter.utility.newsletter import INewsletterUtility
from rer.newsletter.utility.newsletter import OK
from rer.newsletter.utility.newsletter import UNHANDLED
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
            logger.exception(
                'unhandled error subscribing %s %s',
                newsletter,
                email
            )
            self.errors = _(
                u'generic_problem_delete_user',
                default=u'Problem with delete of user from newsletter'
            )
            status = UNHANDLED
            IStatusMessage(self.request).addStatusMessage(
                dmf(self.errors + '. status: ' + str(status)), 'error')
            return

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
            logger.exception(
                'unhandled error on export of user %s',
                newsletter
            )
            self.errors = _(
                u'generic_problem_export_file',
                default=u'Problem with export of user to file'
            )
            status = UNHANDLED
            IStatusMessage(self.request).addStatusMessage(
                dmf(self.errors + '. status: ' + str(status)), 'error')
            return

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
            logger.exception(
                'unhandled error on export of user %s',
                newsletter
            )
            self.errors = u'Problem with export'
            status = UNHANDLED
            IStatusMessage(self.request).addStatusMessage(
                dmf(self.errors + '. status: ' + str(status)), 'error')

        if status == OK:
            return userList
