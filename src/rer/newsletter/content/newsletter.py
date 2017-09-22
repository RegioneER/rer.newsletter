# -*- coding: utf-8 -*-
from zope.interface import implements
from rer.newsletter.interfaces import INewsletter
from plone.app.contenttype.content import Folder


class Newsletter(Folder):
    implements(INewsletter)
