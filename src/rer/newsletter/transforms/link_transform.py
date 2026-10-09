# -*- coding: utf-8 -*-
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
    r"""(<a\b[^>]*?\bhref\s*=\s*)(["'])(.*?)\2""", re.I | re.S
)


def is_matomo_tracking_enabled():
    """Matomo is configured for this instance: MATOMO_SITE_ID env var is set
    (same value used by the Volto frontend). Buildout default is a literal "".
    """
    return bool(os.environ.get("MATOMO_SITE_ID", "").strip().strip("\"'"))


def get_content_short_name(path, base_path):
    """Return the short name of the linked content: last path segment,
    ignoring views and traversers (@@download/file, @@images/..., ++api++).
    """
    if base_path and (path == base_path or path.startswith(base_path + "/")):
        path = path[len(base_path) :]
    segments = []
    for segment in path.split("/"):
        if segment.startswith("@") or segment.startswith("++"):
            break
        if segment:
            segments.append(segment)
    if not segments:
        return "home"
    return unquote(segments[-1])


def add_tracking_url_params(url, message, channel_url, base_urls):
    """Return the url with Matomo params, or unchanged if it does not point
    to the portal.
    """
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https"):
        return url
    bases = [urlsplit(x) for x in base_urls]
    base = [x for x in bases if x.netloc.lower() == parts.netloc.lower()]
    if not base:
        return url
    query = parse_qsl(parts.query, keep_blank_values=True)
    if any(key == "mtm_campaign" for key, value in query):
        # already tracked by hand
        return url
    if channel_url and parts.path.rstrip("/") == urlsplit(
        channel_url
    ).path.rstrip("/"):
        # unsubscribe link
        return url

    channel = message.get_channel()
    query.extend(
        [
            ("mtm_campaign", message.getId()),
            ("mtm_source", channel.getId() if channel is not None else ""),
            ("mtm_medium", "email"),
            (
                "mtm_content",
                get_content_short_name(
                    path=parts.path, base_path=base[0].path.rstrip("/")
                ),
            ),
        ]
    )
    return urlunsplit(parts._replace(query=urlencode(query)))


def add_tracking_params(text, message, source_link, destination_link):
    """Add Matomo tracking params to all portal links in the given html."""
    base_urls = [x for x in (destination_link, source_link) if x]
    channel = message.get_channel()
    channel_url = ""
    if channel is not None:
        channel_url = channel.absolute_url()
        if source_link and destination_link:
            channel_url = re.sub(source_link, destination_link, channel_url)

    def replace(match):
        href = html.unescape(match.group(3))
        new_href = add_tracking_url_params(
            url=href,
            message=message,
            channel_url=channel_url,
            base_urls=base_urls,
        )
        if new_href == href:
            return match.group(0)
        return "{prefix}{quote}{href}{quote}".format(
            prefix=match.group(1),
            quote=match.group(2),
            href=html.escape(new_href, quote=True),
        )

    return HREF_RE.sub(replace, text)


# capire come usare questa classe
@implementer(ITransform)
class link_transform(object):
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
        if destination_link.endswith("/"):
            destination_link = destination_link[:-1]
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
        if IMessage.providedBy(message) and is_matomo_tracking_enabled():
            orig = add_tracking_params(
                orig,
                message=message,
                source_link=source_link,
                destination_link=destination_link,
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
