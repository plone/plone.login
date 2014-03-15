import unittest2 as unittest
from zope.component import getMultiAdapter

from plone.login.testing import \
    PLONE_LOGIN_INTEGRATION_TESTING


class TestViews(unittest.TestCase):

    layer = PLONE_LOGIN_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_resetpassword_view(self):
        view = getMultiAdapter((self.portal, self.request),
                               name="reset-password")
        view = view.__of__(self.portal)
        self.failUnless(view())
