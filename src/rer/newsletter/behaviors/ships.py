from zope.interface import Interface
from zope.interface import alsoProvides


class IShips(Interface):
    ''' Marker interface for ships object '''


alsoProvides(IShips)
