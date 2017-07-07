# -*- coding: utf-8 -*-
from plone import api
from plone.login.testing import PLONE_LOGIN_FUNCTIONAL_TESTING
from plone.login.testing import PLONE_LOGIN_INTEGRATION_TESTING
from plone.testing.z2 import Browser
from zope.component import getMultiAdapter
from plone.login.browser.login_help import RequestResetPassword
from plone.login.browser.login_help import RequestUsername
import unittest
import transaction


class TestLoginHelp(unittest.TestCase):
    layer = PLONE_LOGIN_INTEGRATION_TESTING

    def setUp(self):
        self.request = self.layer['request']
        self.portal = self.layer['portal']

    def test_view(self):
        view = getMultiAdapter((self.portal, self.request), name='login-help')
        self.assertTrue(view())

    def test_view_form(self):
        view = getMultiAdapter((self.portal, self.request), name='login-help')
        form = view.form(view, self.request)
        self.assertEqual(form.subforms, [])
        form.update()
        self.assertEqual(len(form.subforms), 2)
        reset_password = form.subforms[0]
        self.assertTrue(isinstance(reset_password, RequestResetPassword))
        self.assertTrue(reset_password())
        request_username = form.subforms[1]
        self.assertTrue(isinstance(request_username, RequestUsername))
        self.assertTrue(request_username())

    def test_request_reset_password(self):
        view = getMultiAdapter((self.portal, self.request), name='login-help')
        form = view.form(view, self.request)
        form.update()
        reset_password = form.subforms[0]
        reset_password.handleResetPassword(reset_password, None)
        # the field reset_password is required
        self.assertEqual(reset_password.status, u'There were some errors.')
        # reset error message
        reset_password.status = ''

        self.request['form.widgets.reset_password'] = u'test'
        reset_password.handleResetPassword(reset_password, None)
        self.assertEqual(reset_password.status, '')
        self.assertEqual(len(self.portal.MailHost.messages), 0)
        # no mail was sent since the user does not exist
        self.request['form.widgets.reset_password'] = u'test'

        member = api.user.get('test_user_1_')
        email = 'foo@plone.org'
        member.setMemberProperties({'email': email})
        self.request['form.widgets.reset_password'] = u'test_user_1_'
        reset_password.handleResetPassword(reset_password, None)
        self.assertEqual(reset_password.status, '')
        self.assertEqual(len(self.portal.MailHost.messages), 1)
        message = self.portal.MailHost.messages[0]
        self.assertIn('To: foo@plone.org', message)
        self.assertIn('http://nohost/plone/passwordreset/', message)


class TestLoginHelpFunctional(unittest.TestCase):

    layer = PLONE_LOGIN_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.browser = Browser(self.layer['app'])

    def test_login_help_view(self):
        self.browser.open('http://nohost/plone/login')
        self.browser.getLink('Get help').click()
        self.assertEqual(self.browser.url, 'http://nohost/plone/@@login-help')

        member = api.user.get('test_user_1_')
        email = 'foo@plone.org'
        member.setMemberProperties({'email': email})
        transaction.commit()
        # validaton error of empty required field
        self.browser.getControl(name='form.buttons.reset').click()
        self.assertEqual(self.browser.url, 'http://nohost/plone/@@login-help')

        self.browser.getControl(name='form.widgets.reset_password').value = 'nonexistinguser'  # noqa: E501
        self.browser.getControl(name='form.buttons.reset').click()
        self.assertEqual(self.browser.url, 'http://nohost/plone/@@login-help')
        # message appears even though no email was sent
        self.assertIn(
        'An email has been sent with instructions on how to reset your password.', self.browser.contents)  # noqa: E501
        self.assertEqual(len(self.portal.MailHost.messages), 0)

        self.browser.getControl(
            name='form.widgets.reset_password').value = 'test_user_1_'
        self.browser.getControl(name='form.buttons.reset').click()
        self.assertIn(
            'An email has been sent with instructions on how to reset your password.', self.browser.contents)  # noqa: E501
        # message was actually sent
        self.assertEqual(len(self.portal.MailHost.messages), 1)
