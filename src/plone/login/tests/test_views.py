import unittest2 as unittest
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from plone.login.interfaces import IPloneLoginLayer
from plone.login.testing import \
    PLONE_LOGIN_INTEGRATION_TESTING

FORM_ID = 'login'

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

    #def test_form_update(self):
        #self._setup_authenticator_request()
        #self.request['form.widgets.program_type'] = [u'Family child care home']
        #self.request['form.widgets.program_length'] = [u'Half Day']
        #self.request['form.widgets.child_ages'] = [
            #u'0-12 months',
            #u'13-24 months',
            #u'2-5 years']
        #self.request['form.widgets.formula_served'] = u'No'
        #self.request['form.widgets.snacks_served'] = u'Yes'
        #self.request["form.buttons.submit"] = u"Whatever"
        #form = self.portal.restrictedTraverse(FORM_ID)
        #form.update()

        ## data, errors = resetForm.extractData()
        #data, errors = form.extractData()
        #self.assertEqual(len(errors), 0)
