from plone.dexterity.browser import add
from z3c.form import button
from zope.component import getUtility

# logger
from rer.newsletter import logger

# utility
from rer.newsletter.utility.newsletter import INewsletterUtility
from rer.newsletter.utility.newsletter import UNHANDLED
from rer.newsletter.utility.newsletter import OK


class AddForm(add.DefaultAddForm):

    # button handler
    @button.buttonAndHandler(u'Salva', name='save')
    def handleAdd(self, action):
        data, errors = self.extractData()

        # validazione dei campi della form
        # calcolo id della newsletter che viene creata
        # chiamo l'utility per la creazione della newsletter
        try:
            # get newsletter mail from form
            newsletter = u'newsletter@example.org'  # TODO
            api = getUtility(INewsletterUtility)
            status = api.addNewsletter(newsletter)

            # da sistemare inserimento
            self.createAndAdd(data)
        except:
            logger.exception('unhandled error adding newsletter %s %s',
                             newsletter)
            self.errors = u"Problem with adding"
            status = UNHANDLED

        if status == OK:
            self.status = u"Thank you very much!"
        else:
            self.status = u"Ouch .... {}".format(status)



class AddView(add.DefaultAddView):
    form = AddForm
