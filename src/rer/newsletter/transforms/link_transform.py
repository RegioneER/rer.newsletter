# -*- coding: utf-8 -*-
from Products.PortalTransforms.interfaces import ITransform
from zope.interface import implementer
import premailer


# capire come usare questa classe
@implementer(ITransform)
class link_transform(object):
    """
    apply style to newsletter mail and tranforms link from internal to esternal
    """
    __name__ = "link_transform"
    inputs = ('text/html', )
    output = "text/mail"

    def name(self):
        return self.__name__

    def convert(self, orig, data, **kwargs):

        orig = premailer.transform(orig)

        return orig


def register():
    return link_transform()
