# -*- coding: utf-8 -*-
from plone.login.interfaces import IPloneLoginLayer
from plone.login.testing import PLONE_LOGIN_INTEGRATION_TESTING
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
import unittest


class TestViews(unittest.TestCase):

    layer = PLONE_LOGIN_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        alsoProvides(self.request, IPloneLoginLayer)

    def test_resetpassword_view(self):
        view = getMultiAdapter((self.portal, self.request),
                               name='reset-password')
        self.assertTrue(view())

    def test_loggedout_view(self):
        view = getMultiAdapter((self.portal, self.request),
                               name='logged-out')
        self.assertTrue(view())
