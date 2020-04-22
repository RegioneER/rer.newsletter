# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from rer.newsletter.adapter.sender import IChannelSender
from rer.newsletter.testing import RER_NEWSLETTER_INTEGRATION_TESTING
from zope.component import getMultiAdapter

import unittest


class TestSenderAdapter(unittest.TestCase):
    """Test that rer.newsletter is properly installed."""

    layer = RER_NEWSLETTER_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.channel = api.content.create(
            container=self.portal, type='Channel', title='Example channel'
        )

        self.message = api.content.create(
            container=self.channel, type='Message', title='Message foo'
        )

        self.adapter = getMultiAdapter(
            (self.channel, self.request), IChannelSender
        )

    def test_skip(self):
        self.assertTrue(True)
