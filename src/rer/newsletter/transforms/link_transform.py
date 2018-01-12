# -*- coding: utf-8 -*-
from lxml import etree
from plone import api
from Products.PortalTransforms.interfaces import ITransform
from rer.newsletter.browser.settings import ISettingsSchema
from zope.interface import implementer

import premailer


# capire come usare questa classe
@implementer(ITransform)
class link_transform(object):
    """
    convert all source_link in destination_link and apply all style
    """
    __name__ = 'link_transform'
    inputs = ('text/html', )
    output = 'text/mail'

    def __init__(self, name=None):
        self.config_metadata = {
            'inputs': (
                'list',
                'Inputs',
                'Input(s) MIME type. Change with care.'
            ),
        }
        if name:
            self.__name__ = name

    def name(self):
        return self.__name__

    def convert(self, orig, data, **kwargs):
        orig = premailer.transform(orig)

        # come riprendo gli elementi dal control panel
        source_link = api.portal.get_registry_record(
            'source_link', ISettingsSchema)
        if not source_link:
            source_link = api.portal.get().absolute_url()

        destination_link = api.portal.get_registry_record(
            'destination_link', ISettingsSchema)

        tree = etree.HTML(orig)
        tagList = tree.xpath('//a')
        for tag in tagList:
            href = tag.get('href')
            href = href.replace(source_link, destination_link)
            tag.set('href', href)

        data.setData(etree.tostring(tree))
        return data


def register():
    return link_transform()
