# -*- coding: utf-8 -*-
from rer.newsletter import newsletterMessageFactory as _
from plone.supermodel import model
from zope import schema
from zope.interface import alsoProvides
from plone.autoform.interfaces import IFormFieldProvider

# fields
from plone.app.textfield import RichText as RichTextField
from plone.app.z3cform.widget import RichTextFieldWidget
from plone.autoform import directives as form

# constraint
from zope.interface import Invalid
import re


def mailValidation(mail):

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

    model.fieldset(
        "Newsletter's fields",
        label=_(u"Newsletter's Fields"),
        fields=[
                'sender_name',
                'sender_email',
                'subject_email',
                'response_email',
                'header',
                'footer',
                'css_style',
                'idNewsletter',
               ]
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
        # constraint=mailValidation
    )

    subject_email = schema.TextLine(
        title=_("subject_email", default="Subject's email"),
        description=_("description_subject_mail",
                      default="Subject for newsletter's message"),
        required=False
    )

    response_email = schema.TextLine(
        title=_("response_email", default="Response's email"),
        description=_("description_response_email",
                      default="Response email of newsletter"),
        required=False,
        # constraint=mailValidation
    )

    header = RichTextField(
        title=_("header_newsletter", default="Header of message"),
        description=_("description_header_newsletter",
                      "Header for message of this newsletter"),
        required=False,
    )
    form.widget('header', RichTextFieldWidget)

    footer = RichTextField(
        title=_("footer_newsletter", default="Footer of message"),
        description=_("description_footer_newsletter",
                      "Footer for message of this newsletter"),
        required=False,
    )
    form.widget('footer', RichTextFieldWidget)

    css_style = schema.Text(
        title=_("css_style", default="CSS Style"),
        description=_("description_css_style",
                      default="style for mail"),
        required=False
    )

    # probabilemente un campo che va nascosto
    idNewsletter = schema.TextLine(
        title=_("idNewsletter", default="Newsletter's ID"),
        description=_("description_IDNewsletter",
                      "Newsletter's ID"),
        required=False
    )


alsoProvides(INewsletter, IFormFieldProvider)
