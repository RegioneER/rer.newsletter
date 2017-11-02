# -*- coding: utf-8 -*-
from plone.dexterity.browser import add
from z3c.form import button
from zope.component import getUtility

from rer.newsletter import logger

# utility
from rer.newsletter.utility.newsletter import UNHANDLED
from rer.newsletter.utility.newsletter import OK

# unique identifier
from plone.uuid.interfaces import IUUIDGenerator

# messaggi standard della form di dexterity
from Products.statusmessages.interfaces import IStatusMessage

# messageFactory
from rer.newsletter import newsletterMessageFactory as _


class AddForm(add.DefaultAddForm):

    # button handler
    @button.buttonAndHandler(u'Salva', name='save')
    def handleAdd(self, action):
        status = UNHANDLED
        data, errors = self.extractData()

        # controllo se presente l'id della newsletter
        if not data['INewsletter.id_newsletter']:
            generator = getUtility(IUUIDGenerator)
            uuid = generator()
            newsletter = data['INewsletter.id_newsletter'] = uuid

        # validazione dei campi della form
        # calcolo id della newsletter che viene creata
        # chiamo l'utility per la creazione della newsletter
        response = IStatusMessage(self.request)
        try:
            # TODO
            # devo tenere comunque la chiamata ?
            # se non uso mailman questo non serve
            # api = getUtility(INewsletterUtility)
            # status = api.addNewsletter(data['INewsletter.idNewsletter'])

            obj = self.createAndAdd(data)

            if obj:
                self._finishedAdd = True
                status = OK

                # setto il messaggio di inserimento andato a buon fine
                response.add(
                    _(u"add_newsletter", default="Newsletter Created"),
                    type=u'info'
                )
            else:
                status = u"Ouch .... {}".format(status)
                response.add(status, type=u'error')

        except Exception:
            logger.exception(
                'unhandled error adding newsletter %s',
                newsletter
            )
            errors = _(
                u"generic_problem_add_newsletter",
                default=u"Problem with add of newsletter"
            )
            status = UNHANDLED

        if status == UNHANDLED:
            response.add(errors + '. status: ' + str(status), type=u'error')


class AddView(add.DefaultAddView):
    form = AddForm
