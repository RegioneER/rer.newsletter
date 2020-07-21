# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from rer.newsletter.adapter.subscriptions import IChannelSubscriptions
from rer.newsletter.testing import RER_NEWSLETTER_INTEGRATION_TESTING
from rer.newsletter.utils import ALREADY_SUBSCRIBED
from rer.newsletter.utils import INEXISTENT_EMAIL
from rer.newsletter.utils import INVALID_SECRET
from rer.newsletter.utils import MAIL_NOT_PRESENT
from rer.newsletter.utils import OK
from zope.component import getMultiAdapter
from zope.interface import Invalid

import unittest
import json


class TestSubscriptionsAdapter(unittest.TestCase):
    """Test on the 'subscriptions' adapter """

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
        self.assertEqual(status, OK)
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
        self.assertEqual(status, ALREADY_SUBSCRIBED)

    def test_cant_activate_subscription_with_wrong_token(self):
        status, token = self.subscribers_adapter.subscribe('foo@foo.com')
        subscribers = self.subscribers_adapter.channel_subscriptions
        self.assertEqual(subscribers['foo@foo.com']['is_active'], False)

        status, res = self.subscribers_adapter.activateUser('xyz')
        self.assertEqual(res, None)
        self.assertEqual(status, INVALID_SECRET)

    def test_activate_subscription_with_token(self):
        status, token = self.subscribers_adapter.subscribe('foo@foo.com')
        subscribers = self.subscribers_adapter.channel_subscriptions
        self.assertEqual(subscribers['foo@foo.com']['is_active'], False)

        status, res = self.subscribers_adapter.activateUser(token)
        subscribers = self.subscribers_adapter.channel_subscriptions
        self.assertEqual(res, 'foo@foo.com')
        self.assertEqual(status, OK)
        self.assertEqual(subscribers['foo@foo.com']['is_active'], True)

    def test_cant_delete_subscription_with_wrong_token(self):
        status, token = self.subscribers_adapter.subscribe('foo@foo.com')
        self.assertEqual(
            len(self.subscribers_adapter.channel_subscriptions.keys()), 1
        )

        status, res = self.subscribers_adapter.deleteUserWithSecret('xyz')
        self.assertEqual(res, None)
        self.assertEqual(status, INVALID_SECRET)

    def test_cant_delete_subscription_with_wrong_email(self):
        status, token = self.subscribers_adapter.subscribe('foo@foo.com')
        self.assertEqual(
            len(self.subscribers_adapter.channel_subscriptions.keys()), 1
        )

        status = self.subscribers_adapter.deleteUser('bar@bar.com')
        self.assertEqual(status, MAIL_NOT_PRESENT)

    def test_delete_subscription_with_email(self):
        status, token = self.subscribers_adapter.subscribe('foo@foo.com')
        self.assertEqual(
            len(self.subscribers_adapter.channel_subscriptions.keys()), 1
        )

        status = self.subscribers_adapter.deleteUser('foo@foo.com')
        self.assertEqual(status, OK)
        self.assertEqual(
            len(self.subscribers_adapter.channel_subscriptions.keys()), 0
        )

    def test_delete_subscription_with_token(self):
        status, token = self.subscribers_adapter.subscribe('foo@foo.com')
        self.assertEqual(
            len(self.subscribers_adapter.channel_subscriptions.keys()), 1
        )

        status, res = self.subscribers_adapter.deleteUserWithSecret(
            secret=token
        )
        self.assertEqual(res, 'foo@foo.com')
        self.assertEqual(status, OK)
        self.assertEqual(
            len(self.subscribers_adapter.channel_subscriptions.keys()), 0
        )

    def test_add_user_required_mail(self):
        self.assertRaises(TypeError, self.subscribers_adapter.addUser)

    def test_add_user_with_mail(self):
        token = self.subscribers_adapter.addUser('foo@foo.com')

        subscribers = self.subscribers_adapter.channel_subscriptions
        self.assertEqual(len(subscribers.keys()), 1)
        self.assertEqual(subscribers['foo@foo.com']['is_active'], True)
        self.assertEqual(token, 1)

    def test_unsubscribe_user_required_mail(self):
        self.assertRaises(TypeError, self.subscribers_adapter.unsubscribe)

    def test_unsubscribe_user_with_mail(self):
        self.subscribers_adapter.addUser('foo@foo.com')
        self.assertEqual(
            len(self.subscribers_adapter.channel_subscriptions.keys()), 1
        )
        subscribers = self.subscribers_adapter.channel_subscriptions
        status, token = self.subscribers_adapter.unsubscribe('foo@foo.com')

        self.assertEqual(subscribers['foo@foo.com']['token'], token)
        self.assertEqual(len(subscribers.keys()), 1)

    def test_unsubscribe_user_with_wrong_mail(self):
        self.subscribers_adapter.addUser('foo@foo.com')
        self.assertEqual(
            len(self.subscribers_adapter.channel_subscriptions.keys()), 1
        )

        status, token = self.subscribers_adapter.unsubscribe('bar@bar.com')

        self.assertEqual(status, INEXISTENT_EMAIL)

    def test_export_users_list(self):
        res, token = self.subscribers_adapter.exportUsersList()
        self.assertEqual(res, '[]')

        self.subscribers_adapter.subscribe('foo@foo.com')
        self.subscribers_adapter.subscribe('bar@bar.com')

        res, token = self.subscribers_adapter.exportUsersList()
        res_json = json.loads(res)
        self.assertEqual(len(res_json), 2)

    def test_import_users_list(self):
        self.assertEqual(
            len(self.subscribers_adapter.channel_subscriptions.keys()), 0
        )
        self.subscribers_adapter.importUsersList(
            ['foo@foo.com', 'bar@bar.com']
        )
        self.assertEqual(
            len(self.subscribers_adapter.channel_subscriptions.keys()), 2
        )

    def test_import_users_list_with_wrong_mail(self):
        self.assertEqual(
            len(self.subscribers_adapter.channel_subscriptions.keys()), 0
        )
        self.subscribers_adapter.importUsersList(['foo@foo.com', 'bar'])
        self.assertEqual(
            len(self.subscribers_adapter.channel_subscriptions.keys()), 1
        )
