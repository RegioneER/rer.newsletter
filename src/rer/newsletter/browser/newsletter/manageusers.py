from zope.interface import Interface, implements
from Products.Five import BrowserView

from Products.CMFPlone.resources import add_bundle_on_request

import json


class IManageUsers(Interface):
    pass


class ManageUsers(BrowserView):
    implements(IManageUsers)

    def __init__(self, context, request):
        self.context = context
        self.request = request

        add_bundle_on_request(self.request, 'datatables')

    def exportUsersListAsFile(self):
        # predisporre download del file
        import pdb; pdb.set_trace()
        pass

    def exportUsersListAsJson(self):
        # questa funzione andra a chiedere all'unitily di mailman
        # gli utenti da listare
        # torna dati formattati per datatables

        response = []

        element = {}
        element['id'] = 1
        element['Emails'] = 'filippo.campi@redturtle.it'
        response.append(element)

        element = {}
        element['id'] = 2
        element['Emails'] = 'giacomo.monari@redturtle.it'
        response.append(element)

        return json.dumps(response)
