# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from plone.app.z3cform.interfaces import IPloneFormLayer
from plone.login.interfaces import IPloneLoginLayer
from plone.login.testing import PLONE_LOGIN_INTEGRATION_TESTING
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
import re
import unittest

FORM_ID = 'login'


class TestLoginForm(unittest.TestCase):

    layer = PLONE_LOGIN_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.mt = getToolByName(self.portal, 'portal_membership')
        # suitable for testing z3c.form views
        alsoProvides(self.request, IPloneFormLayer)
        alsoProvides(self.request, IPloneLoginLayer)

    def test_login_view(self):
        view = getMultiAdapter((self.portal, self.request),
                               name='login')
        self.assertTrue(view())

    def _setup_authenticator_request(self):
        self.request.set('REQUEST_METHOD', 'POST')
        authenticator = getMultiAdapter((self.portal, self.request),
                                        name=u'authenticator')
        html = authenticator.authenticator()
        token = re.search('value="(.*)"', html).groups()[0]
        self.request.set('_authenticator', token)

    def test_form_update(self):
        self._setup_authenticator_request()
        self.request['__ac_name'] = u'test'
        self.request['__ac_password'] = u'secret'
        self.request['form.widgets.came_from'] = [u'']
        form = self.portal.restrictedTraverse(FORM_ID)
        form.update()

        data, errors = form.form_instance.extractData()
        self.assertEqual(len(errors), 0)

    def test_failsafe_login_form(self):
        view = getMultiAdapter((self.portal, self.request),
                               name='failsafe_login_form')
        html = view()
        self.assertNotIn('main-container', html)

    def test_failsafe_login_form_update(self):
        self._setup_authenticator_request()
        self.request['__ac_name'] = u'test'
        self.request['__ac_password'] = u'secret'
        self.request['form.widgets.came_from'] = [u'']
        form = self.portal.restrictedTraverse('failsafe_login_form')
        form.update()

        data, errors = form.extractData()
        self.assertEqual(len(errors), 0)
