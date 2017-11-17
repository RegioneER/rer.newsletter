# -*- coding: utf-8 -*-
from Products.Five import BrowserView


class MessagePreview(BrowserView):
    """ view for message preview """

    def getMessageStyle(self):
        newsletter = self.context.aq_parent
        return newsletter.css_style

    def getMessagePreview(self):
        newsletter = self.context.aq_parent
        body = ''

        body = newsletter.header.output if newsletter.header else u''
        body += self.context.text.output if self.context.text else u''
        body += newsletter.footer.output if newsletter.footer else u''

        return body
