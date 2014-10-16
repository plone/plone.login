# -*- coding: utf-8 -*-
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.login.interfaces import IPloneLoginLayer
from plone.login.interfaces import IRedirectAfterLogin
from plone.login.testing import PLONE_LOGIN_FUNCTIONAL_TESTING
from plone.testing.z2 import Browser
from zope.interface import Interface
from zope.interface import alsoProvides
from zope.interface import implements
import unittest


class AfterLoginAdapter(object):

    implements(IRedirectAfterLogin)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, came_from=None):
        return 'http://nohost/plone/sitemap'


class TestRedirectAfterLogin(unittest.TestCase):

    layer = PLONE_LOGIN_FUNCTIONAL_TESTING

    def setUp(self):
        # Make sure our browserlayer is applied
        alsoProvides(IPloneLoginLayer)
        self.browser = Browser(self.layer['app'])

    def test_redirect_to_portal_if_no_adapter_nor_came_from(self):
        self.browser.open('http://nohost/plone/login')
        self.browser.getLink('Log in').click()
        self.assertEqual(self.browser.url, 'http://nohost/plone/login')

        self.browser.getControl('Login Name').value = TEST_USER_NAME
        self.browser.getControl('Password').value = TEST_USER_PASSWORD
        self.browser.getControl('Log in').click()

        self.assertIn('You are now logged in.', self.browser.contents)
        self.assertEqual(self.browser.url,
                         'http://nohost/plone',
                         'Successful login did not redirect to the homepage '
                         'when came_from was not defined.')

        # Now log out.
        self.browser.getLink('Log out').click()

        self.assertIn('You have been logged out.',
                      self.browser.contents,
                      'Logout status message not displayed.')

    def test_redirect_to_came_from_if_no_adapter_found(self):
        self.browser.open('http://nohost/plone/login')
        self.browser.getLink('Log in').click()
        self.assertEqual(self.browser.url, 'http://nohost/plone/login')

        self.browser.getControl('Login Name').value = TEST_USER_NAME
        self.browser.getControl('Password').value = TEST_USER_PASSWORD
        self.browser.getControl(name='came_from').value = \
            'http://nohost/plone/contact-info'

        self.browser.getControl('Log in').click()

        self.assertIn('You are now logged in.', self.browser.contents)
        self.assertEqual(self.browser.url,
                         'http://nohost/plone/contact-info',
                         'Successful login did not redirect to the came_from.')

        # Now log out.
        self.browser.getLink('Log out').click()

        self.assertIn('You have been logged out.',
                      self.browser.contents,
                      'Logout status message not displayed.')

    def test_redirect_to_adapter_result(self):
        # Register our redirect adapter
        from zope.component import getGlobalSiteManager
        gsm = getGlobalSiteManager()
        gsm.registerAdapter(AfterLoginAdapter,
                            (Interface, IPloneLoginLayer))

        self.browser.open('http://nohost/plone/login')
        self.browser.getLink('Log in').click()
        self.assertEqual(self.browser.url, 'http://nohost/plone/login')

        self.browser.getControl('Login Name').value = TEST_USER_NAME
        self.browser.getControl('Password').value = TEST_USER_PASSWORD
        self.browser.getControl(name='came_from').value = \
            'http://nohost/plone/contact-info'

        self.browser.getControl('Log in').click()

        gsm.unregisterAdapter(AfterLoginAdapter,
                              (Interface, IPloneLoginLayer))

        self.assertIn('You are now logged in.', self.browser.contents)
        self.assertEqual(self.browser.url,
                         'http://nohost/plone/sitemap',
                         'Successful login did not use the adapter for '
                         'redirect.')

        # Now log out.
        self.browser.getLink('Log out').click()

        self.assertIn('You have been logged out.',
                      self.browser.contents,
                      'Logout status message not displayed.')
