# -*- coding: utf-8 -*-
import unittest2 as unittest
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from plone.login.interfaces import IPloneLoginLayer
from plone.login.testing import \
    PLONE_LOGIN_INTEGRATION_TESTING


class TestViews(unittest.TestCase):

    layer = PLONE_LOGIN_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        alsoProvides(self.request, IPloneLoginLayer)

    def test_resetpassword_view(self):
        view = getMultiAdapter((self.portal, self.request),
                               name="reset-password")
        view = view.__of__(self.portal)
        self.failUnless(view())

    def test_loggedout_view(self):
        view = getMultiAdapter((self.portal, self.request),
                               name="logged-out")
        view = view.__of__(self.portal)
        self.failUnless(view())
