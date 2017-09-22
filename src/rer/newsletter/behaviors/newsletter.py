# -*- coding: utf-8 -*-
from rer.newsletter import newsletterMessageFactory as _
from plone.supermodel import model
from zope import schema
from zope.interface import alsoProvides
from plone.autoform.interfaces import IFormFieldProvider


class INewsletter(model.Schema):
    """
    Define fields for newsletter behaviors
    """

    active = schema.Bool(
        title=_("active_newsletter", default="Active newsletter"),
        description=_("description_active_newsletter",
                      default="Make newsletter active")
    )


alsoProvides(INewsletter, IFormFieldProvider)
