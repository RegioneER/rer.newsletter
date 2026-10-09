# -*- coding: utf-8 -*-
"""Add Matomo campaign tracking parameters to newsletter links."""
from plone import api
from plone.i18n.normalizer import idnormalizer
from rer.newsletter.browser.settings import ISettingsSchema
from urllib.parse import parse_qsl
from urllib.parse import urlencode
from urllib.parse import urlsplit
from urllib.parse import urlunsplit

import html
import os
import re


HREF_RE = re.compile(
    r"""(<a\b[^>]*?\bhref\s*=\s*)(["'])(.*?)\2""", re.I | re.S
)


def is_matomo_tracking_enabled():
    """Matomo must be configured for this instance (MATOMO_SITE_ID env var,
    same value used by the Volto frontend) and tracking enabled in the
    newsletter settings.
    """
    site_id = os.environ.get("MATOMO_SITE_ID", "").strip().strip("\"'")
    if not site_id:
        return False
    return api.portal.get_registry_record(
        "matomo_tracking_enabled", interface=ISettingsSchema, default=True
    )


def _get_content_param(path, portal_path, channel):
    """Return the mtm_content value for the given url path (relative to the
    portal), or None if the link points to the channel itself.
    """
    mode = api.portal.get_registry_record(
        "matomo_content_param", interface=ISettingsSchema, default="id"
    )
    segments = [x for x in path.split("/") if x]
    if not segments:
        return "home"
    catalog = api.portal.get_tool("portal_catalog")
    # strip trailing segments (views, @@download/file, @@images/...) until
    # we find a content
    for i in range(len(segments), 0, -1):
        brains = catalog.unrestrictedSearchResults(
            path={"query": "/".join([portal_path] + segments[:i]), "depth": 0}
        )
        if not brains:
            continue
        brain = brains[0]
        if channel is not None and brain.UID == channel.UID():
            return None
        if mode == "portal_type":
            return idnormalizer.normalize(brain.portal_type)
        return brain.getId
    return segments[-1]


def add_tracking_url_params(url, message, channel, base_url):
    """Return the url with Matomo params, or unchanged if it does not point
    to the portal.
    """
    parts = urlsplit(url)
    base = urlsplit(base_url)
    if parts.scheme not in ("http", "https"):
        return url
    if parts.netloc.lower() != base.netloc.lower():
        return url
    base_path = base.path.rstrip("/")
    if parts.path != base_path and not parts.path.startswith(base_path + "/"):
        return url
    query = parse_qsl(parts.query, keep_blank_values=True)
    if any(key == "mtm_campaign" for key, value in query):
        # already tracked by hand
        return url

    portal_path = "/".join(api.portal.get().getPhysicalPath())
    content = _get_content_param(
        path=parts.path[len(base_path) :],
        portal_path=portal_path,
        channel=channel,
    )
    if content is None:
        return url

    query.extend(
        [
            ("mtm_campaign", message.getId()),
            ("mtm_source", channel.getId() if channel is not None else ""),
            ("mtm_medium", "email"),
            ("mtm_content", content),
        ]
    )
    return urlunsplit(parts._replace(query=urlencode(query)))


def add_tracking_params(text, message, channel, base_url):
    """Add Matomo tracking params to all portal links in the given html."""
    if not base_url:
        base_url = api.portal.get().absolute_url()

    def replace(match):
        href = html.unescape(match.group(3))
        new_href = add_tracking_url_params(
            url=href, message=message, channel=channel, base_url=base_url
        )
        if new_href == href:
            return match.group(0)
        return "{prefix}{quote}{href}{quote}".format(
            prefix=match.group(1),
            quote=match.group(2),
            href=html.escape(new_href, quote=True),
        )

    return HREF_RE.sub(replace, text)
