# -*- coding: utf-8 -*-
import unittest2 as unittest
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from plone.browserlayer.utils import registered_layers

from plone.login.testing import \
    PLONE_LOGIN_INTEGRATION_TESTING


class TestInstall(unittest.TestCase):

    layer = PLONE_LOGIN_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.registry = getUtility(IRegistry)
        #self.jqueryui_settings = self.registry.forInterface(IJQueryUIPlugins)
        self.qi_tool = getToolByName(self.portal, 'portal_quickinstaller')

    def test_product_is_installed(self):
        """ Validate that our products GS profile has been run and the product
            installed
        """
        pid = 'plone.login'
        installed = [p['id'] for p in self.qi_tool.listInstalledProducts()]
        self.assertTrue(pid in installed,
                        'package appears not to have been installed')

    def test_js_available(self):
        pass

    def test_addon_layer(self):
        layers = [l.getName() for l in registered_layers()]
        self.assertTrue('IPloneLoginLayer' in layers,
                        'add-on layer was not installed')



