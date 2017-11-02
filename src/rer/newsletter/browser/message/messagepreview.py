# -*- coding: utf-8 -*-
from Products.Five import BrowserView


class MessagePreview(BrowserView):
    """ view for message preview """

    def getMessageStyle(self):
        newsletter = self.context.aq_parent
        return newsletter.css_style

    def getMessagePreview(self):
        newsletter = self.context.aq_parent
        messagePreview = ''

        messagePreview = newsletter.header.raw
        messagePreview += self.context.text.raw
        messagePreview += newsletter.footer.raw

        return messagePreview
