import unittest2 as unittest

from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.testing.z2 import Browser
from zope.component import getMultiAdapter
from zope.interface import alsoProvides

from plone.login.interfaces import IPloneLoginLayer
from plone.login.testing import PLONE_LOGIN_FUNCTIONAL_TESTING


class TestViews(unittest.TestCase):

    layer = PLONE_LOGIN_FUNCTIONAL_TESTING

    def setUp(self):
        # Make sure our browserlayer is applied
        alsoProvides(IPloneLoginLayer)
        self.browser = Browser(self.layer['app'])

    def test_login_with_bad_credentials(self):
        self.browser.open('http://nohost/plone/login')
        self.browser.getLink('Log in').click()
        self.assertEqual(self.browser.url, 'http://nohost/plone/login')

        self.browser.getControl('Login Name').value = TEST_USER_NAME
        self.browser.getControl('Password').value = 'wrongpassword'
        self.browser.getControl('Log in').click()

        self.assertIn("Login failed", self.browser.contents)
        self.assertEqual(self.browser.url, 'http://nohost/plone/login_form')
