import unittest
import re
from zope.interface import alsoProvides
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from plone.app.z3cform.interfaces import IPloneFormLayer
from plone.login.interfaces import IPloneLoginLayer
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
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

    def test_register_view(self):
        view = getMultiAdapter((self.portal, self.request),
                               name="register")
        view = view.__of__(self.portal)
        self.failUnless(view())
