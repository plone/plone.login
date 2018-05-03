# -*- coding: utf-8 -*-
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import MOCK_MAILHOST_FIXTURE
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2
from zope.configuration import xmlconfig


class PloneloginLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import plone.login
        xmlconfig.file(
            'configure.zcml',
            plone.login,
            context=configurationContext
        )

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'plone.login:default')


PLONE_LOGIN_FIXTURE = PloneloginLayer()
PLONE_LOGIN_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_LOGIN_FIXTURE, MOCK_MAILHOST_FIXTURE),
    name='PloneloginLayer:Integration'
)
PLONE_LOGIN_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_LOGIN_FIXTURE, MOCK_MAILHOST_FIXTURE, z2.ZSERVER_FIXTURE),
    name='PloneloginLayer:Functional'
)
