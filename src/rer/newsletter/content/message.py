# -*- coding: utf-8 -*-
from zope.interface import implements
from rer.newsletter.interfaces import IMessage
from plone.app.contenttype.content import Document


class Message(Document):
    implements(IMessage)
