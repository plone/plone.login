# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.Five.browser import BrowserView
from Products.PlonePAS import interfaces as plonepas_interfaces
from Products.PluggableAuthService.interfaces import plugins as pas_interfaces
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.statusmessages.interfaces import IStatusMessage
from plone.login.auth import logger
from plone.login.auth.interfaces import IOAuthPlugin
from plone.login.interfaces import ILoginSettings
from plone.registry.interfaces import IRegistry
from zExceptions import NotFound
from zExceptions import Redirect
from zope.component import getUtility
from zope.interface import implementer
import hashlib
import json
import requests
import transaction
import urllib

SESSION_KEY = hashlib.sha512('plone.login').hexdigest()


class OAuthException(Exception):

    def __init__(self, message):
        self.__doc__ = message


class OAuthProvider(BrowserView):
    """OAuth Provider"""

    @property
    def providers(self):
        settings = getUtility(IRegistry).forInterface(ILoginSettings)
        return settings.oauth_providers

    @property
    def session(self):
        if SESSION_KEY not in self.request.SESSION.keys():
            self.request.SESSION[SESSION_KEY] = {}

        return self.request.SESSION[SESSION_KEY]

    @property
    def redirect_uri(self):
        return '{0:s}/@@{1:s}/{2:s}'.format(
            self.context.absolute_url(), self.__name__, self.provider)

    @property
    def authorization_url(self):
        return self.config['auth_url']

    @property
    def authorization_args(self):
        return dict(
            client_id=self.config['client_id'],
            response_type=self.config['response_type'],
            redirect_uri=self.redirect_uri,
        )

    def request_authorization(self):
        raise Redirect('{0:s}?{1:s}'.format(
            self.authorization_url,
            urllib.urlencode(self.authorization_args, doseq=True)
        ))

    @property
    def token_url(self):
        return self.config['token_url']

    def token_args(self, returned_code):
        return dict(
            client_id=self.config['client_id'],
            client_secret=self.config['client_secret'],
            redirect_uri=self.redirect_uri,
            code=returned_code,
            grant_type=self.config['grant_type'],
        )

    @property
    def request_token(self):
        return self.request.get(self.config['response_code_variable'])

    def request_access_token(self, returned_code):
        r = requests.post(
            self.config['token_url'], data=self.token_args(returned_code))
        try:
            data = json.loads(r.text)
            assert r.ok
        except AssertionError:
            raise OAuthException(data.get('error_description', 'Unknown'))
        except Exception as e:
            raise OAuthException(e.__doc__)

        self.set_token(data['access_token'])

    def set_token(self, token):
        self.session['token'] = token

    def request_profile(self):
        r = requests.get(self.config['profile_url'], params={
            self.config['access_token_variable']: self.session.get('token'),
        })

        if r.ok:
            user_data = json.loads(r.text)
            self.set_user_data(user_data)
            return user_data

    def set_user_data(self, data):
        self.session['userId'] = data['username']
        self.session['userEmail'] = data['email']
        self.session['userFullname'] = data.get('name') or data['username']
        self.session['userLogin'] = data['username']
        self.session['userProvider'] = self.provider

    def do_handshake(self):
        if not self.request_token:
            # 1. To request the authorization token, you should visit the
            # /oauth/authorize endpoint.
            return self.request_authorization()
        else:
            # 2. To request the access token we have to use the returned code
            # and exchange it for an access token.
            try:
                self.request_access_token(self.request_token)
            except OAuthException as e:
                IStatusMessage(self.request).add(e.__doc__, type='error')
            else:
                self.request_profile()
                IStatusMessage(self.request).add('Success', type='info')

        responseProfile = self.request_profile()
        logger.info(responseProfile)

        transaction.commit()
        raise Redirect(self.context.absolute_url())

    def __getitem__(self, provider):
        if provider not in self.providers:
            raise NotFound

        self.provider = provider
        self.config = self.providers[provider]

        return self.do_handshake()

    def __call__(self):
        raise NotFound


@implementer(
    IOAuthPlugin,
    pas_interfaces.ICredentialsResetPlugin,
    pas_interfaces.IExtractionPlugin,
    pas_interfaces.IAuthenticationPlugin,
    pas_interfaces.IGroupsPlugin,
    pas_interfaces.IPropertiesPlugin,
    plonepas_interfaces.plugins.IMutablePropertiesPlugin,
    plonepas_interfaces.plugins.IUserManagement)
class OAuthPlugin(BasePlugin):
    """Glue layer for making node.ext.ldap available to PAS.
    """
    security = ClassSecurityInfo()
    meta_type = 'OAuth Plugin'

    # Tell PAS not to swallow our exceptions
    _dont_swallow_my_exceptions = False

    def __init__(self, id, title=None):
        self._setId(id)
        self.title = title

    @security.private
    def authenticateCredentials(self, credentials):
        user_login = credentials.get('userlogin')
        user_id = credentials.get('userid')

        if not (user_id or user_login):
            return

        if credentials.get('src') != self.getId():
            return

        logger.info('Login {0:s}'.format(user_id))

        # TODO
        # if self.config.get('registration'):
        #     user = api.user.get(user_id=user_id)
        #     if user:
        #         user_id = login = user.getId()
        #         request = self.REQUEST
        #         response = request.RESPONSE
        #         self._getPAS().updateCredentials(request, response, login, '')
        #         return (user_id, login)
        #     else:
        #         return

        return (user_id, user_login)

    @security.private
    def resetCredentials(self, request, response):
        session = request.SESSION
        if SESSION_KEY in session:
            session.delete(SESSION_KEY)

    @security.private
    def extractCredentials(self, request):
        session = request.SESSION.get(SESSION_KEY)
        if session:
            return dict(
                src=self.getId(),
                provider=session.get('userProvider'),
                userid=session.get('userId'),
                userfullname=session.get('userFullname'),
                userlogin=session.get('userLogin'),
                useremail=session.get('userEmail'),
            )

        return {}

    def getGroupsForPrincipal(self, principal, request=None):
        return ('Authenticated', )

    def getPropertiesForUser(self, principal, request=None):
        session = request.SESSION.get(SESSION_KEY)
        return dict(
            userid=session.get('userId'),
            fullname=session.get('userFullname'),
            email=session.get('userEmail'),
        )

InitializeClass(IOAuthPlugin)
