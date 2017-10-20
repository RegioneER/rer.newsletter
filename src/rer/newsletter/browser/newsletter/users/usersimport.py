from zope.component import getUtility
from zope.interface import Interface
from zope import schema
from z3c.form import button, form, field
from plone.namedfile.field import NamedFile

from rer.newsletter.utility.newsletter import INewsletterUtility
from rer.newsletter import logger
from rer.newsletter.utility.newsletter import OK, UNHANDLED, INVALID_NEWSLETTER

import StringIO
import csv

# messageFactory
from rer.newsletter import newsletterMessageFactory as _


class IUsersImport(Interface):

    userListFile = NamedFile(
        title=_(u"title_users_list_file", default=u"Users List File"),
        description=_(u"description_file", default=u"File must be a CSV"),
        required=True
    )

    # se questo e ceccato allora i dati non vengono inseriti
    emptyList = schema.Bool(
        title=_(u"title_empty_list", default=u"Empties users list"),
        description=_(u"description_empty_list",
                      default=u"Empties newsletter users list"),
        required=False
    )

    # se e ceccato sia questo dato che 'emptyList' allora do precedenza a emptyList
    removeSubscribers = schema.Bool(
        title=_(u"title_remove_subscribers",
                default=u"Remove subscribers of the list"),
        description=_(u"description_remove_subscribers",
                      default=u"Remove users of CSV from newsletter's subscribers"),
        required=False
    )

    headerLine = schema.Bool(
        title=_(u"title_header_line",
                default=u"Header Line"),
        description=_(u"description_header_line",
                      default=_(u"if CSV File contains a header line")),
        required=False
    )

    separator = schema.TextLine(
        title=_(u"title_separator",
                default=u"CSV separator"),
        description=_(u"description_separator",
                      default=_(u"Separator of CSV file")),
        required=True
    )


class UsersImport(form.Form):

    ignoreContext = True
    fields = field.Fields(IUsersImport)

    def processCSV(self, data, headerline, separator):
        io = StringIO.StringIO(data)

        reader = csv.reader(
            io,
            delimiter=separator.encode('ascii', 'ignore'),
            dialect="excel",
            quotechar="\""
        )

        index = 0
        if headerline:
            header = reader.next()

            # leggo solo la colonna della email
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
            # TODO sistemare la gestione delle eccezioni
            # devo uscire al primo status fallito

            # prendo la connessione con il server mailman
            api_newsletter = getUtility(INewsletterUtility)

            # devo svuotare la lista di utenti della newsletter
            if data['emptyList']:
                self.status = api_newsletter.emptyNewsletterUsersList(
                    self.context.idNewsletter
                )

            csv_file = data['userListFile'].data
            # esporto la lista di utenti dal file
            usersList = self.processCSV(
                csv_file,
                data['headerLine'],
                data['separator']
            )

            # controllo se devo eliminare l'intera lista di utenti
            # invece di importarla
            if data['removeSubscribers'] and not data['emptyList']:
                # chiamo l'api per rimuovere l'intera lista di utenti
                self.status = api_newsletter.deleteUserList(
                    usersList,
                    self.context.idNewsletter
                )

            else:
                # mi connetto con le api di mailman
                self.status = api_newsletter.importUsersList(
                    usersList,
                    self.context.idNewsletter
                )

        except:
            logger.exception(
                'unhandled error users import'
            )
            self.errors = u"Problem with subscribe"
            self.status = UNHANDLED

        if self.status == OK:
            self.status = u"Thank you very much!"
        else:
            self.status = u"Ouch .... {}".format(self.status)

        return
