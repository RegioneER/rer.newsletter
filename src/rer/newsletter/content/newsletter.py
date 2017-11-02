# -*- coding: utf-8 -*-
from plone.app.contenttypes.content import Folder
from rer.newsletter.interfaces import INewsletter
from zope.interface import implementer


@implementer(INewsletter)
class Newsletter(Folder):
    pass
