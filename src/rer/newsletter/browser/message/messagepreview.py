# -*- coding: utf-8 -*-
from datetime import datetime
from Products.Five import BrowserView
from rer.newsletter.behaviors.ships import IShippable
from rer.newsletter.content.channel import Channel
from rer.newsletter.interfaces import IBlocksToHtml
from zope.component import getUtility


DEFAULT_STYLES = """
.block.image {
  clear:both;
}
.block.align.right img {
    margin-left: 1em;
    float: right;
}
.block.align.left img {
    margin-right: 1em;
    float: left;
}
"""


class MessagePreview(BrowserView):
    """view for message preview"""

    def getMessageStyle(self):
        channel = None
        for obj in self.context.aq_chain:
            if isinstance(obj, Channel):
                channel = obj
                break
        return DEFAULT_STYLES + channel.css_style

    @property
    def channel(self):
        for obj in self.context.aq_chain:
            if isinstance(obj, Channel):
                return obj
        return None

    def getMessageHeader(self):
        header = getattr(self.channel, "header", "")
        if not header:
            return ""

        blocks_converter = getUtility(IBlocksToHtml)
        html = blocks_converter(
            context=self.context,
            blocks=header.get("blocks", {}),
            blocks_layout=header.get("blocks_layout", {}),
        )

        return f"""
            <tr id="newsletter-header">
                <td align="left" colspan="2">
                    {html}
                </td>
            </tr>
        """

    def getMessageFooter(self):
        footer = getattr(self.channel, "footer", "")
        if not footer:
            return ""

        blocks_converter = getUtility(IBlocksToHtml)
        html = blocks_converter(
            context=self.context,
            blocks=footer.get("blocks", {}),
            blocks_layout=footer.get("blocks_layout", {}),
        )
        return f"""
            <tr id="newsletter-footer">
                <td align="left" colspan="2">
                    {html}
                </td>
            </tr>
        """

    def getMessageSubHeader(self):
        return f"""
            <tr>
                <td align="left" colspan="2">
                  <div class="newsletterTitle">
                    <h1>{self.context.title}</h1>
                  </div>
                </td>
            </tr>
        """

    def getMessageContent(self):
        return f"""
            <tr>
                <td align="left" colspan="2">
                    {IShippable(self.context).message_content}
                </td>
            </tr>
        """

    def getMessagePreview(self):
        channel = None
        for obj in self.context.aq_chain:
            if isinstance(obj, Channel):
                channel = obj
                break
        if channel:
            body = ""
            body = channel.header if channel.header else ""
            body += f"""

                <tr>
                    <td align="left">
                        <div class="gmail-blend-screen">
                        <div class="gmail-blend-difference">
                            <div class="divider"></div>
                        </div>
                        </div>
                        <div class="newsletterTitle">
                        <h1>{self.context.title}</h1>
                        <h4 class="newsletterDate">{
                            datetime.today().strftime('Newsletter %d %B %Y')
                        }</h4>
                    </div>

                    </td>
                </tr>
                <tr>
                    <td align="left">
                     {IShippable(self.context).message_content}
                    </td>
                </tr>

            """
            body += channel.footer if channel.footer else ""

        return body
