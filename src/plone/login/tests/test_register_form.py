# -*- coding: utf-8 -*-
import unittest
import re
from zope.interface import alsoProvides
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from plone.app.z3cform.interfaces import IPloneFormLayer
from plone.login.interfaces import IPloneLoginLayer

#from plone import api
from plone.login.testing import \
    PLONE_LOGIN_INTEGRATION_TESTING

FORM_ID = 'register'


class TestRegisterForm(unittest.TestCase):

    layer = PLONE_LOGIN_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.mt = getToolByName(self.portal, 'portal_membership')
        # suitable for testing z3c.form views
        alsoProvides(self.request, IPloneFormLayer)
        alsoProvides(self.request, IPloneLoginLayer)

    def _setup_authenticator_request(self):
        self.request.set('REQUEST_METHOD', 'POST')
        authenticator = getMultiAdapter((self.portal, self.request),
                                        name=u"authenticator")
        html = authenticator.authenticator()
        token = re.search('value="(.*)"', html).groups()[0]
        self.request.set('_authenticator', token)

    def test_register_view(self):
        view = getMultiAdapter((self.portal, self.request),
                               name="register")
        view = view.__of__(self.portal)
        self.assertTrue(view())

    def test_form_update(self):
        self._setup_authenticator_request()
        self.request['username'] = u'test_user'
        self.request['email'] = u'secret'
        self.request['password'] = u'12345'
        self.request['password_confirm'] = u'12345'
        form = self.portal.restrictedTraverse(FORM_ID)
        form.form_instance.update()

        data, errors = form.form_instance.extractData()
        self.assertEqual(len(errors), 0)

    def test_user_registered(self):
        self._setup_authenticator_request()
        username = u'tester'
        self.request['username'] = username
        self.request['email'] = u'tester@example.org'
        self.request['password'] = u'12345'
        self.request['password_confirm'] = u'12345'
        form = self.portal.restrictedTraverse(FORM_ID)
        form.form_instance.update()
        form.form_instance.handleRegister(form.form_instance, 'http://nohost')

        self.assertIn(username, self.mt.listMemberIds())
