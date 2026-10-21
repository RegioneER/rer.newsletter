# from lxml import etree
from plone import api
from premailer import Premailer
from Products.PortalTransforms.interfaces import ITransform
from rer.newsletter.browser.settings import ISettingsSchema
from rer.newsletter.interfaces import IMessage
from urllib.parse import parse_qsl
from urllib.parse import unquote
from urllib.parse import urlencode
from urllib.parse import urlsplit
from urllib.parse import urlunsplit
from zope.interface import implementer

import html
import os
import re


HREF_RE = re.compile(
    r"""(<a\b[^>]*?\bhref\s*=\s*)(["'])(.*?)\2""", re.IGNORECASE | re.DOTALL
)


def get_content_short_name(path):
    """Return the short name of the linked content: last path segment,
    ignoring views and traversers (@@download/file, @@images/..., ++api++).
    """
    segments = []
    for segment in path.split("/"):
        if segment.startswith(("@", "++")):
            break
        if segment:
            segments.append(segment)
    return unquote(segments[-1]) if segments else "home"


def add_tracking_params(text, message, portal_url):
    """Add Matomo tracking params to all links that point to the portal
    (same domain of portal_url, the one links have been rewritten to).
    """
    host = urlsplit(portal_url).netloc.lower()
    params = [
        ("mtm_campaign", message.getId()),
        ("mtm_source", message.get_channel().getId()),
        ("mtm_medium", "email"),
    ]

    def replace(match):
        parts = urlsplit(html.unescape(match.group(3)))
        if (
            parts.scheme not in ("http", "https")
            or parts.netloc.lower() != host
        ):
            return match.group(0)
        query = parse_qsl(parts.query, keep_blank_values=True)
        query += params + [("mtm_content", get_content_short_name(parts.path))]
        href = urlunsplit(parts._replace(query=urlencode(query)))
        return "{prefix}{quote}{href}{quote}".format(
            prefix=match.group(1),
            quote=match.group(2),
            href=html.escape(href, quote=True),
        )

    return HREF_RE.sub(replace, text)


# capire come usare questa classe
@implementer(ITransform)
class link_transform:
    """
    convert all source_link in destination_link and apply all style
    """

    __name__ = "link_transform"
    inputs = ("text/html",)
    output = "text/mail"

    def __init__(self, name=None):
        self.config_metadata = {
            "inputs": (
                "list",
                "Inputs",
                "Input(s) MIME type. Change with care.",
            ),
        }
        if name:
            self.__name__ = name

    def name(self):
        return self.__name__

    def convert(self, orig, data, **kwargs):
        p = Premailer(orig, strip_important=False)
        orig = p.transform()

        source_link = api.portal.get_registry_record(
            "source_link", ISettingsSchema
        )
        if not source_link:
            source_link = api.portal.get().absolute_url()

        # If volto frontend_domain is set, use it as destination link
        try:
            destination_link = api.portal.get_registry_record(
                "volto.frontend_domain", default=""
            )
        except KeyError:
            destination_link = ""
        destination_link = destination_link.removesuffix("/")
        if not destination_link:
            # otherwise, use the newsletter one
            destination_link = api.portal.get_registry_record(
                "destination_link", ISettingsSchema
            )

        # non è questo il modo migliore per fare il replace...
        # 1. non serve usare re.sub ma basta il replace di string
        # 2. forse sarebbe più corretto usare un metodo di lxml
        if source_link and destination_link:
            orig = re.sub(source_link, destination_link, orig)

        # newsletter messages pass themselves as context: add Matomo tracking
        # params to portal links
        message = kwargs.get("context")
        if IMessage.providedBy(message):
            is_matomo_tracking_enabled = bool(
                os.environ.get("MATOMO_SITE_ID", "").strip().strip("\"'")
            )
            if is_matomo_tracking_enabled:
                orig = add_tracking_params(
                    orig,
                    message=message,
                    portal_url=destination_link or source_link,
                )

        # tree = etree.HTML(orig)
        # tagList = tree.xpath('//a')
        # for tag in tagList:
        #     href = tag.get('href')
        #     href = href.replace(source_link, destination_link)
        #      tag.set('href', href)
        # data.setData(etree.tostring(tree))
        data.setData(orig)

        return data


def register():
    return link_transform()
