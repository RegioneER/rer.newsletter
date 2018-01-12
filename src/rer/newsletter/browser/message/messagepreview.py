# -*- coding: utf-8 -*-
from Products.Five import BrowserView


class MessagePreview(BrowserView):
    """ view for message preview """

    def getMessageStyle(self):
        channel = self.context.aq_parent
        return channel.css_style

    def getMessagePreview(self):
        channel = self.context.aq_parent
        body = ''

        body = channel.header.output if channel.header else u''
        body += self.context.text.output if self.context.text else u''
        body += channel.footer.output if channel.footer else u''

        return body
