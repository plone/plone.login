# -*- coding: utf-8 -*-
from plone.login.testing import PLONE_LOGIN_INTEGRATION_TESTING
from Products.CMFCore.utils import getToolByName

import unittest


class TestInstall(unittest.TestCase):

    layer = PLONE_LOGIN_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.qi_tool = getToolByName(self.portal, 'portal_quickinstaller')

    def test_product_is_installed(self):
        """ Validate that our products GS profile has been run and the product
            installed
        """
        pid = 'plone.login'
        installed = [p['id'] for p in self.qi_tool.listInstalledProducts()]
        self.assertTrue(pid in installed,
                        'package appears not to have been installed')
