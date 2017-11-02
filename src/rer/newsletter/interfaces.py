# -*- coding: utf-8 -*-
'''Module where all interfaces, events and exceptions live.'''
from plone import schema
from plone.app.textfield import RichText as RichTextField
from plone.app.z3cform.widget import RichTextFieldWidget
from plone.autoform import directives as form
from plone.supermodel import model
from rer.newsletter import _
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

import uuid


def default_id_newsletter():
    return unicode(uuid.uuid4())


class IRerNewsletterLayer(IDefaultBrowserLayer):
    '''Marker interface that defines a browser layer.'''


# newsletter
class INewsletter(Interface):
    ''' Marker interface that define a newsletter '''


class INewsletterSchema(model.Schema):
    ''' a dexterity schema for newsletter '''

    # model.fieldset(
    #     'Newsletter's fields',
    #     label=_(u'Newsletter's Fields'),
    #     fields=[
    #             'sender_name',
    #             'sender_email',
    #             'subject_email',
    #             'response_email',
    #             'header',
    #             'footer',
    #             'css_style',
    #             'id_newsletter',
    #            ]
    # )

    sender_name = schema.TextLine(
        title=_('sender_name', default='Sender Fullname'),
        description=_('description_sender_name',
                      default='Fullname of sender'),
        required=False,
    )

    sender_email = schema.Email(
        title=_('sender_email', default='Sender email'),
        description=_('description_sender_email',
                      default='Email of sender'),
        required=True,
    )

    subject_email = schema.TextLine(
        title=_('subject_email', default='Subject email'),
        description=_('description_subject_mail',
                      default='Subject for newsletter message'),
        required=False
    )

    response_email = schema.Email(
        title=_('response_email', default='Response email'),
        description=_('description_response_email',
                      default='Response email of newsletter'),
        required=False,
    )

    header = RichTextField(
        title=_('header_newsletter', default='Header of message'),
        description=_('description_header_newsletter',
                      default='Header for message of this newsletter'),
        required=False,
        default=u'',
    )
    form.widget('header', RichTextFieldWidget)

    footer = RichTextField(
        title=_('footer_newsletter', default='Footer of message'),
        description=_('description_footer_newsletter',
                      default='Footer for message of this newsletter'),
        required=False,
        default=u'',
    )
    form.widget('footer', RichTextFieldWidget)

    css_style = schema.Text(
        title=_('css_style', default='CSS Style'),
        description=_('description_css_style', default='style for mail'),
        required=False,
        default=u'',
    )

    # probabilemente un campo che va nascosto
    id_newsletter = schema.TextLine(
        title=_('idNewsletter', default='Newsletter ID'),
        description=_('description_IDNewsletter', default='Newsletter ID'),
        required=True,
        defaultFactory=default_id_newsletter,
    )


class IMessage(Interface):
    ''' Marker interface that define a message '''


class IMessageSchema(model.Schema):
    ''' a dexterity schema for message '''
