# -*- coding: utf-8 -*-
from Products.PortalTransforms.interfaces import ITransform
from zope.interface import implementer


# capire come usare questa classe
@implementer(ITransform)
class Link_Transform(object):

    def __init__(self):
        import pdb
        pdb.set_trace()

        pass


def register():
    return Link_Transform()
