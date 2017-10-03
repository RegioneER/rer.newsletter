from zope.interface import Interface, implements
from Products.Five import BrowserView

from Products.CMFPlone.resources import add_bundle_on_request


class IManageUsers(Interface):
    pass


class ManageUsers(BrowserView):
    implements(IManageUsers)

    def __init__(self, context, request):
        self.context = context
        self.request = request

        add_bundle_on_request(self.request, 'datatables')
