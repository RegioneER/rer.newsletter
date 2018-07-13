# -*- coding: utf-8 -*-
from ..interfaces import INotifyOnSubscribe
from ..interfaces import INotifyOnUnsubscribe
from plone.contentrules.rule.interfaces import IRuleElementData
from zope.interface import implementer


@implementer(INotifyOnSubscribe, IRuleElementData)
class NotifyOnSubscribe(object):
    pass


@implementer(INotifyOnUnsubscribe, IRuleElementData)
class NotifyOnUNsubscribe(object):
    pass
