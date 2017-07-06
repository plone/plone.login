# -*- coding: utf-8 -*-
from DateTime import DateTime
from plone.login import MessageFactory as _
from plone.login.browser.login_help import template_path
from plone.login.interfaces import ILoginForm
from plone.login.interfaces import ILoginFormSchema
from plone.login.interfaces import IPloneLoginLayer
from plone.login.interfaces import IRedirectAfterLogin
from plone.registry.interfaces import IRegistry
from plone.z3cform import layout
from plone.z3cform.templates import FormTemplateFactory
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import ISecuritySchema
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from z3c.form import field
from z3c.form import form
from z3c.form.interfaces import HIDDEN_MODE
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.interface import implementer

import urllib


@implementer(ILoginForm)
class LoginForm(form.EditForm):
    """ Implementation of the login form """

    fields = field.Fields(ILoginFormSchema)

    id = 'LoginForm'
    label = _('heading_login_form', default=u'Log in')
    description = _('description_login_form', default=u'Long time no see.')

    ignoreContext = True
    prefix = ''

    def _get_auth(self):
        try:
            return self.context.acl_users.credentials_cookie_auth
        except AttributeError:
            try:
                return self.context.cookie_authentication
            except AttributeError:
                pass

    def updateWidgets(self):
        auth = self._get_auth()

        if auth:
            fieldname_name = auth.get('name_cookie', '__ac_name')
            fieldname_password = auth.get('pw_cookie', '__ac_password')
        else:
            fieldname_name = '__ac_name'
            fieldname_password = '__ac_password'

        self.fields['ac_name'].__name__ = fieldname_name
        self.fields['ac_password'].__name__ = fieldname_password

        super(LoginForm, self).updateWidgets(prefix='')

        if self.use_email_as_login():
            self.widgets[fieldname_name].label = _(u'label_email',
                                                   default=u'E-mail')
        self.widgets['came_from'].mode = HIDDEN_MODE

    def updateActions(self):
        super(LoginForm, self).updateActions()
        self.actions['login'].addClass('context')

    @button.buttonAndHandler(_('Log in'), name='login')
    def handleLogin(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        membership_tool = getToolByName(self.context, 'portal_membership')
        if membership_tool.isAnonymousUser():
            self.request.response.expireCookie('__ac', path='/')
            if self.use_email_as_login():
                IStatusMessage(self.request).addStatusMessage(_(
                    u'Login failed. Both email address and password are case '
                    u'sensitive, check that caps lock is not enabled.'
                ), 'error')
            else:
                IStatusMessage(self.request).addStatusMessage(_(
                    u'Login failed. Both login name and password are case '
                    u'sensitive, check that caps lock is not enabled.'
                ), 'error')
            return

        member = membership_tool.getAuthenticatedMember()
        login_time = member.getProperty('login_time', '2000/01/01')
        if not isinstance(login_time, DateTime):
            login_time = DateTime(login_time)
        initial_login = login_time == DateTime('2000/01/01')
        if initial_login:
            # TODO: Redirect if this is initial login
            pass

        must_change_password = member.getProperty('must_change_password', 0)

        if must_change_password:
            # TODO: This user needs to change his password
            pass

        membership_tool.loginUser(self.request)

        IStatusMessage(self.request).addStatusMessage(_(
            u'statusmessage_logged_in', default=u'You are now logged in.'
        ), 'info')

        came_from = None
        if data['came_from']:
            came_from = data['came_from']

        self.redirect_after_login(came_from)

    def redirect_after_login(self, came_from=None):
        adapter = queryMultiAdapter((self.context, self.request),
                                    IRedirectAfterLogin)
        if adapter:
            came_from = adapter(came_from)
        else:
            if not came_from:
                came_from = self.context.portal_url()

        self.request.response.redirect(came_from)

    def self_registration_enabled(self):
        registry = queryUtility(IRegistry)
        security_settings = registry.forInterface(
            ISecuritySchema, prefix='plone')
        return security_settings.enable_self_reg

    def use_email_as_login(self):
        registry = queryUtility(IRegistry)
        security_settings = registry.forInterface(
            ISecuritySchema, prefix='plone')
        return security_settings.use_email_as_login


class LoginFormView(layout.FormWrapper):
    form = LoginForm


wrapped_login_template = FormTemplateFactory(
    template_path('login.pt'),
    form=ILoginForm,
    request=IPloneLoginLayer
)


class RequireLoginView(BrowserView):

    def __call__(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name='plone_portal_state')
        portal = portal_state.portal()
        if portal_state.anonymous():
            url = '{0:s}/login'.format(portal.absolute_url())
            came_from = self.request.get('came_from', None)
            if came_from:
                url += '?came_from={0:s}'.format(urllib.quote(came_from))
        else:
            url = '{0:s}/insufficient-privileges'.format(portal.absolute_url())

        self.request.response.redirect(url)


class InsufficientPrivilegesView(BrowserView):

    def request_url(self):
        return self.request.get('came_from')
