# -*- coding: utf-8 -*-
"""Tests for Matomo link tracking in sent messages."""
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from rer.newsletter.browser.settings import ISettingsSchema
from rer.newsletter.testing import RER_NEWSLETTER_INTEGRATION_TESTING
from unittest import mock
from urllib.parse import parse_qs
from urllib.parse import urlsplit

import html
import re
import unittest


class TestMatomoTracking(unittest.TestCase):
    layer = RER_NEWSLETTER_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.channel = api.content.create(
            container=self.portal, type="Channel", title="My channel"
        )
        self.message = api.content.create(
            container=self.channel, type="Message", title="My message"
        )
        self.document = api.content.create(
            container=self.portal, type="Document", title="My document"
        )
        self.portal_url = self.portal.absolute_url()

    def convert(self, text, context=None, site_id="32"):
        with mock.patch.dict("os.environ", {"MATOMO_SITE_ID": site_id}):
            pt = api.portal.get_tool("portal_transforms")
            kwargs = {"context": context} if context is not None else {}
            return pt.convertTo("text/mail", text, **kwargs).getData()

    def get_hrefs(self, text):
        return [html.unescape(x) for x in re.findall(r'href="([^"]*)"', text)]

    def get_params(self, url):
        return {k: v[0] for k, v in parse_qs(urlsplit(url).query).items()}

    def test_internal_link_has_tracking_params(self):
        text = self.convert(
            '<a href="{}">link</a>'.format(self.document.absolute_url()),
            context=self.message,
        )
        url = self.get_hrefs(text)[0]
        self.assertTrue(url.startswith(self.document.absolute_url() + "?"))
        self.assertEqual(
            self.get_params(url),
            {
                "mtm_campaign": "my-message",
                "mtm_source": "my-channel",
                "mtm_medium": "email",
                "mtm_content": "my-document",
            },
        )

    def test_no_tracking_without_env(self):
        text = self.convert(
            '<a href="{}">link</a>'.format(self.document.absolute_url()),
            context=self.message,
            site_id='""',
        )
        self.assertEqual(self.get_hrefs(text), [self.document.absolute_url()])

    def test_no_tracking_if_disabled(self):
        api.portal.set_registry_record(
            "matomo_tracking_enabled", False, interface=ISettingsSchema
        )
        text = self.convert(
            '<a href="{}">link</a>'.format(self.document.absolute_url()),
            context=self.message,
        )
        self.assertEqual(self.get_hrefs(text), [self.document.absolute_url()])

    def test_no_tracking_without_message_context(self):
        text = self.convert(
            '<a href="{}">link</a>'.format(self.document.absolute_url())
        )
        self.assertEqual(self.get_hrefs(text), [self.document.absolute_url()])

    def test_external_and_mailto_links_untouched(self):
        text = self.convert(
            '<a href="https://www.example.com/foo">ext</a>'
            '<a href="mailto:foo@example.com">mail</a>'
            '<a href="#top">anchor</a>',
            context=self.message,
        )
        self.assertEqual(
            self.get_hrefs(text),
            ["https://www.example.com/foo", "mailto:foo@example.com", "#top"],
        )

    def test_existing_params_are_kept(self):
        text = self.convert(
            '<a href="{}?a=1&amp;b=2#section">link</a>'.format(
                self.document.absolute_url()
            ),
            context=self.message,
        )
        self.assertIn("a=1&amp;b=2&amp;mtm_campaign=my-message", text)
        url = self.get_hrefs(text)[0]
        self.assertTrue(url.endswith("#section"))
        params = self.get_params(url)
        self.assertEqual(params["a"], "1")
        self.assertEqual(params["mtm_content"], "my-document")

    def test_view_suffix_resolves_to_content(self):
        text = self.convert(
            '<a href="{}/@@download/file">link</a>'.format(
                self.document.absolute_url()
            ),
            context=self.message,
        )
        url = self.get_hrefs(text)[0]
        self.assertEqual(self.get_params(url)["mtm_content"], "my-document")

    def test_portal_type_content_param(self):
        api.portal.set_registry_record(
            "matomo_content_param", "portal_type", interface=ISettingsSchema
        )
        text = self.convert(
            '<a href="{}">link</a>'.format(self.document.absolute_url()),
            context=self.message,
        )
        url = self.get_hrefs(text)[0]
        self.assertEqual(self.get_params(url)["mtm_content"], "document")

    def test_homepage_link(self):
        text = self.convert(
            '<a href="{}">link</a>'.format(self.portal_url),
            context=self.message,
        )
        url = self.get_hrefs(text)[0]
        self.assertEqual(self.get_params(url)["mtm_content"], "home")

    def test_manually_tracked_link_untouched(self):
        href = "{}?mtm_campaign=custom".format(self.document.absolute_url())
        text = self.convert(
            '<a href="{}">link</a>'.format(href), context=self.message
        )
        self.assertEqual(self.get_hrefs(text), [href])

    def test_channel_link_untouched(self):
        text = self.convert(
            '<a href="{}">unsubscribe</a>'.format(self.channel.absolute_url()),
            context=self.message,
        )
        self.assertEqual(self.get_hrefs(text), [self.channel.absolute_url()])
