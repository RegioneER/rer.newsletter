# -*- coding: utf-8 -*-
from zope.interface import implementer
from zope.interface.interfaces import IObjectEvent
from zope.interface.interfaces import ObjectEvent


class ISubscriptionEvent(IObjectEvent):
    """ Channel subscription event """


class IUnsubscriptionEvent(IObjectEvent):
    """ Channel unsubscription event """


@implementer(ISubscriptionEvent)
class SubscriptionEvent(ObjectEvent):
    """  """


@implementer(IUnsubscriptionEvent)
class UnsubscriptionEvent(ObjectEvent):
    """  """
