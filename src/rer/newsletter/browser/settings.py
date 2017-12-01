# -*- coding: utf-8 -*-
from plone.app.registry.browser import controlpanel
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import Interface
from plone import schema
from zope.component import getUtility
from rer.newsletter.utility.newsletter import INewsletterUtility
from rer.newsletter import _


class ISettingsSchema(Interface):
    """ Schema for newsletter settings"""

    source_link = schema.TextLine(
        title=_(u"source_link", default=u"Link sorgente"),
        description=_(
            u"description_source_link",
            default=u"Indirizzo da sostituire"
        ),
        default=u"applicazioni.regione.emilia-romagna.it",
        required=False
    )

    destination_link = schema.TextLine(
        title=_(u"destination_link", default=u"Link di destinazione"),
        description=_(
            u"description_destination_link",
            default=u"Indirizzo da sostituire"
        ),
        required=False
    )


class NewsletterSettings(controlpanel.RegistryEditForm):
    # template = ViewPageTemplateFile('settings.pt')
    schema = ISettingsSchema
    id = 'NewsletterSettings'
    label = _(u'newsletter_setting', default=u"Newsletters Settings")

    # def getLists(self):
    #
    #     api = getUtility(INewsletterUtility)
    #     return dir(api)


class NewsletterSettingsControlPanel(controlpanel.ControlPanelFormWrapper):

    form = NewsletterSettings
