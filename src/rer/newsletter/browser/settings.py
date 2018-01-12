# -*- coding: utf-8 -*-
from plone.app.registry.browser import controlpanel
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import Interface
from plone import schema
from zope.component import getUtility
from rer.newsletter.utility.channel import IChannelUtility
from rer.newsletter import _


class ISettingsSchema(Interface):
    """ Schema for channel settings"""

    source_link = schema.TextLine(
        title=_(u'source_link', default=u'Link sorgente'),
        description=_(
            u'description_source_link',
            default=u'Indirizzo da sostituire'
        ),
        default=u'applicazioni.regione.emilia-romagna.it',
        required=False
    )

    destination_link = schema.TextLine(
        title=_(u'destination_link', default=u'Link di destinazione'),
        description=_(
            u'description_destination_link',
            default=u'Indirizzo da sostituire'
        ),
        required=False
    )


class ChannelSettings(controlpanel.RegistryEditForm):
    # template = ViewPageTemplateFile('settings.pt')
    schema = ISettingsSchema
    id = 'ChannelSettings'
    label = _(u'channel_setting', default=u'Channel Settings')

    # def getLists(self):
    #
    #     api = getUtility(IChannelUtility)
    #     return dir(api)


class ChannelSettingsControlPanel(controlpanel.ControlPanelFormWrapper):

    form = ChannelSettings
