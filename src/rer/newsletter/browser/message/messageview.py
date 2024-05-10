# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from zope.component import getUtility
from rer.newsletter.interfaces import IBlocksToHtml


class MessageView(BrowserView):
    def get_text(self):
        blocks_converter = getUtility(IBlocksToHtml)
        return blocks_converter(
            context=self.context,
            blocks=getattr(self.context, "blocks", {}),
            blocks_layout=getattr(self.context, "blocks_layout", {}),
        )
