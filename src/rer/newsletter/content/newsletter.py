from zope.interface import implements
from rer.newsletter.interfaces import INewsletter
from plone.dexterity.content import Container


class Newsletter(Container):
    implements(INewsletter)
