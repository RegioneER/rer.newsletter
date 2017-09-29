from plone.dexterity.browser import add
from z3c.form import button
from zope.component import getUtility

# logger
from rer.newsletter import logger

# utility
from rer.newsletter.utility.newsletter import INewsletterUtility
from rer.newsletter.utility.newsletter import UNHANDLED
from rer.newsletter.utility.newsletter import OK

# unique identifier
from plone.uuid.interfaces import IUUIDGenerator


class AddForm(add.DefaultAddForm):

    # button handler
    @button.buttonAndHandler(u'Salva', name='save')
    def handleAdd(self, action):
        data, errors = self.extractData()

        # controllo se presente l'id della newsletter
        if not data['INewsletter.id_newsletter']:
            generator = getUtility(IUUIDGenerator)
            uuid = generator()
            data['INewsletter.id_newsletter'] = uuid

        # validazione dei campi della form
        # calcolo id della newsletter che viene creata
        # chiamo l'utility per la creazione della newsletter
        try:
            api = getUtility(INewsletterUtility)
            status = api.addNewsletter(data['INewsletter.id_newsletter'])

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
