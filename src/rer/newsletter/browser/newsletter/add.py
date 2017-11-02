# -*- coding: utf-8 -*-
from plone.dexterity.browser import add
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button

from rer.newsletter import  _
from rer.newsletter import logger
from rer.newsletter.utility.newsletter import UNHANDLED
from rer.newsletter.utility.newsletter import OK


class AddForm(add.DefaultAddForm):

    # button handler
    @button.buttonAndHandler(u'Salva', name='save')
    def handleAdd(self, action):
        status = UNHANDLED
        data, errors = self.extractData()

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
                response.add(
                    _(u"add_newsletter", default="Newsletter Created"),
                    type=u'info'
                )
            else:
                # TODO: gestire messaggi personalizzati per ogni status
                status = u"Ouch .... {}".format(status)
                response.add(status, type=u'error')
        except:
            logger.exception(
                'unhandled error adding newsletter %s',
                data
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
