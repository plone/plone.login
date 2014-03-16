import unittest2 as unittest
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
                               name="login")
        view = view.__of__(self.portal)
        self.failUnless(view())

    def _setup_authenticator_request(self):
        self.request.set('REQUEST_METHOD', 'POST')
        authenticator = getMultiAdapter((self.portal, self.request),
                                        name=u"authenticator")
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

    def test_user_logged_in(self):
        self._setup_authenticator_request()
        self.request['__ac_name'] = TEST_USER_NAME
        self.request['__ac_password'] = TEST_USER_PASSWORD
        self.request['form.widgets.came_from'] = [u'']
        form = self.portal.restrictedTraverse(FORM_ID)
        form.update()
        form.form_instance.handleLogin(form.form_instance, 'http://nohost')

        #data, errors = form.form_instance.extractData()
        member = self.mt.getAuthenticatedMember()
        self.assertEqual(member.getUserName(), 'test-user')
