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
        response = {}
        data = []
        data.append('filippo.campi@redturtle.it')
        data.append('filippo.campi@redturtle.it')
        data.append('filippo.campi@redturtle.it')
        data.append('filippo.campi@redturtle.it')
        data.append('filippo.campi@redturtle.it')

        response['data'] = data
        return json.dumps(response)
