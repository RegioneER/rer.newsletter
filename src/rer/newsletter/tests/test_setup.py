# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from rer.newsletter.testing import RER_NEWSLETTER_INTEGRATION_TESTING

import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that rer.newsletter is properly installed."""

    layer = RER_NEWSLETTER_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")

    def test_product_installed(self):
        """Test if rer.newsletter is installed."""
        if hasattr(self.installer, "is_product_installed"):
            # Plone 6
            self.assertTrue(self.installer.is_product_installed("rer.newsletter"))
        else:
            # Plone 5
            self.assertTrue(self.installer.isProductInstalled("rer.newsletter"))

    def test_browserlayer(self):
        """Test that IRerNewsletterLayer is registered."""
        from plone.browserlayer import utils
        from rer.newsletter.interfaces import IRerNewsletterLayer

        self.assertIn(IRerNewsletterLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):
    layer = RER_NEWSLETTER_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        if hasattr(self.installer, "uninstall_product"):
            # Plone 6
            self.installer.uninstall_product("rer.newsletter")
        else:
            # Plone 5
            self.installer.uninstallProducts(["rer.newsletter"])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if rer.newsletter is cleanly uninstalled."""
        if hasattr(self.installer, "is_product_installed"):
            # Plone 6
            self.assertFalse(self.installer.is_product_installed("rer.newsletter"))
        else:
            # Plone 5
            self.assertFalse(self.installer.isProductInstalled("rer.newsletter"))

    def test_browserlayer_removed(self):
        """Test that IRerNewsletterLayer is removed."""
        from plone.browserlayer import utils
        from rer.newsletter.interfaces import IRerNewsletterLayer

        self.assertNotIn(IRerNewsletterLayer, utils.registered_layers())
