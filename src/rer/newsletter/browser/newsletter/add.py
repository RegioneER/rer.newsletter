# -*- coding: utf-8 -*-
from plone import api
from plone.dexterity.browser import add
from rer.newsletter import _
from rer.newsletter import logger
from rer.newsletter.utility.newsletter import OK
from rer.newsletter.utility.newsletter import UNHANDLED
from z3c.form import button


class AddForm(add.DefaultAddForm):

    # button handler
    @button.buttonAndHandler(u'Salva', name='save')
    def handleAdd(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        # validazione dei campi della form
        # calcolo id della newsletter che viene creata
        # chiamo l'utility per la creazione della newsletter
        status = UNHANDLED
        try:
            obj = self.createAndAdd(data)
            if obj:
                self._finishedAdd = True
                status = OK
                api.portal.show_message(
                    message=_(u'add_newsletter', default='Newsletter Created'),
                    request=self.request,
                    type=u'info'
                )
            else:
                status = u'Ouch .... {status}'.format(status=status)
                api.portal.show_message(
                    message=status,
                    request=self.request,
                    type=u'error'
                )
        except Exception:
            logger.exception(
                'unhandled error adding newsletter %s',
                data
            )
            self.errors = _(
                u'generic_problem_add_newsletter',
                default=u'Problem with add of newsletter'
            )
            status = UNHANDLED

        if status == UNHANDLED:
            api.portal.show_message(
                message=errors + '. status: ' + str(status),
                request=self.request,
                type=u'error'
            )


class AddView(add.DefaultAddView):
    form = AddForm
