from zope.interface import implements
from rer.newsletter.interfaces import IMessage
from plone.dexterity.content import Container


class Message(Container):
    implements(IMessage)
