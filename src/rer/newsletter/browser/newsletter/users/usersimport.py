from zope.component import getUtility
from zope.interface import Interface
from z3c.form import button, form, field
from plone.namedfile.field import NamedFile

from rer.newsletter.utility.newsletter import INewsletterUtility
from rer.newsletter import logger
from rer.newsletter.utility.newsletter import OK, UNHANDLED

import StringIO
import csv

# messageFactory
from rer.newsletter import newsletterMessageFactory as _


class IUsersImport(Interface):

    userListFile = NamedFile(
        title=_(u"users_list_file", default=u"Users List File"),
        description=_(u"description_file", default=u"File must be a CSV"),
        required=True
    )


class UsersImport(form.Form):

    ignoreContext = True
    fields = field.Fields(IUsersImport)

    def processCSV(self, data):
        io = StringIO.StringIO(data)

        reader = csv.reader(io, delimiter=',', dialect="excel", quotechar='"')

        header = reader.next()

        index = None
        for i in range(0, len(header)):
            if header[i].decode("utf-8") == "email":
                index = i

        if index is None:
            raise RuntimeError("CSV data does not have column:" + "email")

        usersList = []
        for row in reader:
            usersList.append(row[index].decode("utf-8"))

        return usersList

    @button.buttonAndHandler(u"charge")
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        try:

            # TODO
            csv_file = data['userListFile'].data
            # controllo sul file
            usersList = self.processCSV(csv_file)

            # mi connetto con le api di mailman
            api_newsletter = getUtility(INewsletterUtility)
            status = api_newsletter.importUsersList(usersList)

        except:
            logger.exception(
                'unhandled error users import'
            )
            self.errors = u"Problem with subscribe"
            status = UNHANDLED

        if status == OK:
            self.status = u"Thank you very much!"
        else:
            self.status = u"Ouch .... {}".format(status)
