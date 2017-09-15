# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.interface import Interface
from plone.supermodel import model


class IRerNewsletterLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


# newsletter
class INewsletter(Interface):
    ''' Marker interface that define a newsletter '''


class INewsletterSchema(model.Schema):
    ''' a dexterity schema for newsletter '''


# message
class IMessage(Interface):
    ''' Marker interface that define a message '''


class IMessageSchema(model.Schema):
    ''' a dexterity schema for message '''
