# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from senaite.async_ar_add.testing import SENAITE_ASYNC_AR_ADD_INTEGRATION_TESTING  # noqa

import unittest


class TestSetup(unittest.TestCase):
    """Test that senaite.async_ar_add is properly installed."""

    layer = SENAITE_ASYNC_AR_ADD_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if senaite.async_ar_add is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'senaite.async_ar_add'))

    def test_browserlayer(self):
        """Test that ISenaiteAsyncArAddLayer is registered."""
        from senaite.async_ar_add.interfaces import (
            ISenaiteAsyncArAddLayer)
        from plone.browserlayer import utils
        self.assertIn(ISenaiteAsyncArAddLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = SENAITE_ASYNC_AR_ADD_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['senaite.async_ar_add'])

    def test_product_uninstalled(self):
        """Test if senaite.async_ar_add is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'senaite.async_ar_add'))

    def test_browserlayer_removed(self):
        """Test that ISenaiteAsyncArAddLayer is removed."""
        from senaite.async_ar_add.interfaces import \
            ISenaiteAsyncArAddLayer
        from plone.browserlayer import utils
        self.assertNotIn(ISenaiteAsyncArAddLayer, utils.registered_layers())
