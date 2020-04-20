# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from rer.newsletter.adapter.subscriptions import IChannelSubscriptions
from rer.newsletter.testing import RER_NEWSLETTER_INTEGRATION_TESTING
from zope.component import getMultiAdapter
from zope.interface import Invalid

import unittest


class TestSetup(unittest.TestCase):
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

        self.subscribers_adapter = getMultiAdapter(
            (self.channel, self.request), IChannelSubscriptions
        )

    def test_subscribe_raise_exception_for_invalid_email(self):
        self.assertRaises(Invalid, self.subscribers_adapter.subscribe, 'foo')
        self.assertRaises(
            Invalid, self.subscribers_adapter.subscribe, 'foo@foo'
        )

    def test_subscribe_email(self):
        self.assertEqual(self.subscribers_adapter.channel_subscriptions, {})
        status, token = self.subscribers_adapter.subscribe('foo@foo.com')

        subscribers = self.subscribers_adapter.channel_subscriptions
        self.assertEqual(status, 1)
        self.assertNotEqual(subscribers, {})
        self.assertEqual(token, subscribers['foo@foo.com']['token'])
        self.assertEqual(subscribers['foo@foo.com']['is_active'], False)

    def test_subscribe_email_twice_return_error(self):
        self.subscribers_adapter.subscribe('foo@foo.com')

        self.assertEqual(
            len(self.subscribers_adapter.channel_subscriptions.keys()), 1
        )
        status, token = self.subscribers_adapter.subscribe('foo@foo.com')

        self.assertEqual(
            len(self.subscribers_adapter.channel_subscriptions.keys()), 1
        )
        self.assertEqual(token, None)
        self.assertEqual(status, 2)

    def test_activate_subscription(self):
        status, token = self.subscribers_adapter.subscribe('foo@foo.com')
        subscribers = self.subscribers_adapter.channel_subscriptions
        self.assertEqual(subscribers['foo@foo.com']['is_active'], False)

        status, res = self.subscribers_adapter.activateUser('xyz')
        self.assertEqual(res, None)
        self.assertEqual(status, 10)

        status, res = self.subscribers_adapter.activateUser(token)
        subscribers = self.subscribers_adapter.channel_subscriptions
        self.assertEqual(res, 'foo@foo.com')
        self.assertEqual(status, 1)
        self.assertEqual(subscribers['foo@foo.com']['is_active'], True)
