# -*- coding: utf-8 -*-
from plone.tiles import Tile
from plone.z3cform.layout import FormWrapper
from rer.newsletter import _
from z3c.form import button
from z3c.form import field
from z3c.form.form import Form
from zope import schema
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.interface import Interface

import re


class IForm(Interface):
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


class SubscribeTileForm(Form):

    fields = field.Fields(IForm)
    label = _(u'Search for pubblications')
    ignoreContext = True

    @button.buttonAndHandler(_(u'Add', default='Add'))
    def handleApply(self, action):
        pass


class TileFormViewer(FormWrapper):

    form = SubscribeTileForm
    index = ViewPageTemplateFile('SubscribeNewsletterTile.pt')

    # def get_error_message(self):
    #     return self.context.translate(
    #         _(u'End date should be great than start date')
    #     )


class SubscribeNewsletter(Tile):
    """
    Tile for subscribe to newsletter
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.form_wrapper = self.create_form()

    def __call__(self):
        return super(SubscribeNewsletter, self).__call__()

    def create_form(self):
        context = self.context.aq_inner
        # reutrnURL = self.context.absolute_url()
        form = SubscribeTileForm(context, self.request)
        view = TileFormViewer(context, self.request)
        view = view.__of__(context)
        view.form_instance = form
        return view
