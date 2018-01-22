# -*- coding: utf-8 -*-
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from rer.newsletter import _
from zope import schema
from zope.interface import implements

import re


class INewsletterSubscribePortlet(IPortletDataProvider):
    """
    aggiungere i campi allo schema della portlet
    """
    header = schema.TextLine(
        title=_(u'title_portlet_header', default=u'Portlet header'),
        description=_(u'description_portlet_header',
                      default=u'Title of the rendered portlet'),
        constraint=re.compile('[^\s]').match,
        required=False)

    link_to_archive = schema.ASCIILine(
        title=_(u'title_portlet_link', default=u'Details link'),
        description=_(
            u'description_portlet_link',
            default=u'If given, the header and footer will link to this URL.'
        ),
        required=False)

    css_class = schema.TextLine(
        title=_(u'title_css_portlet_class', default=u'Portlet class'),
        description=_(u'description_css_portlet_class',
                      default=u'CSS class to add at the portlet'),
        required=False
    )


class Assignment(base.Assignment):
    implements(INewsletterSubscribePortlet)

    def __init__(self, header=u'', link_to_archive='', css_class=''):
        self.header = header
        self.link_to_archive = link_to_archive
        self.css_class = css_class

    @property
    def title(self):
        if self.header:
            return self.header
        else:
            return u'RER portlet newsletter'


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('subscribe.pt')

    def getPortletClass(self):
        classes = 'portlet NewsletterSubscribePortlet'
        if self.data.css_class:
            classes += ' {0}'.format(self.data.css_class)
        return classes

    def is_subscribable(self):
        if self.context.portal_type == 'Channel'\
                and self.context.is_subscribable:
            return True
        else:
            return False


class AddForm(base.AddForm):
    schema = INewsletterSubscribePortlet

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    schema = INewsletterSubscribePortlet
