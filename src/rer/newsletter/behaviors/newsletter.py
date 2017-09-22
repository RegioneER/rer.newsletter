# -*- coding: utf-8 -*-
from rer.newsletter import newsletterMessageFactory as _
from plone.supermodel import model
from zope import schema
from zope.interface import alsoProvides
from plone.autoform.interfaces import IFormFieldProvider

# constraint
from zope.interface import Invalid
import re


def mailValidation(mailList):

    for mail in mailList:
        # valido la mail
        match = re.match(
            '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$',
            mail
        )
        if match is None:
            raise Invalid(u"Una o piu delle mail inserite non sono valide")
    return True


class INewsletter(model.Schema):
    """
    Define fields for newsletter behaviors
    """

    active = schema.Bool(
        title=_("active_newsletter", default="Active newsletter"),
        description=_("description_active_newsletter",
                      default="Make newsletter active"),
        required=False
    )

    sender_name = schema.TextLine(
        title=_("sender_name", default="Sender's Fullname"),
        description=_("description_sender_name",
                      default="Fullname of sender"),
        required=False
    )

    sender_email = schema.TextLine(
        title=_("sender_email", default="Sender's email"),
        description=_("description_sender_email",
                      default="Email of sender"),
        required=False,
        constraint=mailValidation
    )




alsoProvides(INewsletter, IFormFieldProvider)
