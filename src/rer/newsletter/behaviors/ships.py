from zope.interface import Interface
from zope.interface import alsoProvides


class IShippable(Interface):
    ''' Marker interface for ships object '''


alsoProvides(IShippable)
