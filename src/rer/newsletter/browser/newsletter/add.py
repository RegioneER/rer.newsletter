from plone.dexterity.browser import add
from z3c.form import button

# messaggi standard della form di dexterity
from Products.statusmessages.interfaces import IStatusMessage
from plone.dexterity.i18n import MessageFactory as dmf


class AddForm(add.DefaultAddForm):

    # button handler
    @button.buttonAndHandler(u'Salva', name='save')
    def handleAdd(self, action):
        data, errors = self.extractData()

        # validazione dei campi della form
        # calcolo id della newsletter che viene creata
        # chiamo l'utility per la creazione della newsletter

        obj = self.createAndAdd(data)

        if obj is not None:
            self._finishedAdd = True
            # setto il messaggio di inserimento andato a buon fine
            IStatusMessage(self.request).addStatusMessage(
                dmf(u"Item created"), "info")


class AddView(add.DefaultAddView):
    form = AddForm
