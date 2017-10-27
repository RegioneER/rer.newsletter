# -*- coding: utf-8 -*-
from plone.app.registry.browser import controlpanel
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import Interface
from zope.component import getUtility
from rer.newsletter.utility.newsletter import INewsletterUtility


class ISettingsSchema(Interface):
    """ """


class NewsletterSettings(controlpanel.RegistryEditForm):
    template = ViewPageTemplateFile('settings.pt')
    schema = ISettingsSchema

    def getLists(self):
        api = getUtility(INewsletterUtility)
        return api.lists()
