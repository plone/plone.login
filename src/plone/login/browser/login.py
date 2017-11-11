# -*- coding: utf-8 -*-
from DateTime import DateTime
from plone.app.users.browser.passwordpanel import PasswordPanel
from plone.login import MessageFactory as _
from plone.login.browser.login_help import template_path
from plone.login.interfaces import IForcePasswordChange
from plone.login.interfaces import IInitialLogin
from plone.login.interfaces import ILoginForm
from plone.login.interfaces import ILoginFormSchema
from plone.login.interfaces import IRedirectAfterLogin
from plone.registry.interfaces import IRegistry
from plone.z3cform import layout
from plone.z3cform.templates import FormTemplateFactory
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import ISecuritySchema
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from six.moves.urllib import parse
from z3c.form import button
from z3c.form import field
from z3c.form import form
from z3c.form.interfaces import HIDDEN_MODE
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.interface import implementer


@implementer(ILoginForm)
class LoginForm(form.EditForm):
    """ Implementation of the login form """

    fields = field.Fields(ILoginFormSchema)

    id = 'LoginForm'
    label = _('label_log_in', default=u'Log in')

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
        self.widgets['came_from'].value = self.get_came_from()

    def get_came_from(self):
        came_from = self.request.get('came_from', None)
        if not came_from:
            came_from = self.request.get('HTTP_REFERER', None)
        if came_from:
            url_tool = getToolByName(self.context, 'portal_url')
            if url_tool.isURLInPortal(came_from):
                came_from_id = parse.urlparse(came_from)[2].split('/')[-1]
                # TODO: Scale down this list now that we've removed a lot of
                # templates.
                login_template_ids = ['login',
                                      'login_success',
                                      'login_password',
                                      'login_failed',
                                      'login_form',
                                      'logged_in',
                                      'logout',
                                      'logged-out',
                                      'registered',
                                      'mail_password',
                                      'mail_password_form',
                                      'register',
                                      'require_login',
                                      'member_search_results',
                                      'pwreset_finish',
                                      'localhost']
                if came_from_id not in login_template_ids:
                    return came_from
        return None

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
        must_change_password = member.getProperty('must_change_password', 0)
        login_time = member.getProperty('login_time', '2000/01/01')
        if not isinstance(login_time, DateTime):
            login_time = DateTime(login_time)
        is_initial_login = login_time == DateTime('2000/01/01')

        membership_tool.loginUser(self.request)
        IStatusMessage(self.request).addStatusMessage(_(
            u'you_are_now_logged_in',
            default=u'Welcome! You are now logged in.'), 'info')

        if is_initial_login:
            self.handle_initial_login()

        if must_change_password:
            self.force_password_change()

        came_from = data.get('came_from', None)
        self.redirect_after_login(came_from, is_initial_login)

    def handle_initial_login(self):
        handler = queryMultiAdapter((self.context, self.request),
                                    IInitialLogin)
        if handler:
            handler()
        return

    def force_password_change(self):
        handler = queryMultiAdapter((self.context, self.request),
                                    IForcePasswordChange)
        if handler:
            handler()
        return

    def redirect_after_login(self, came_from=None, is_initial_login=False):
        adapter = queryMultiAdapter((self.context, self.request),
                                    IRedirectAfterLogin)
        if adapter:
            came_from = adapter(came_from, is_initial_login)
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
    form=ILoginForm)


class RequireLoginView(BrowserView):

    def __call__(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name='plone_portal_state')
        portal = portal_state.portal()
        if portal_state.anonymous():
            url = '{0:s}/login'.format(portal.absolute_url())
            came_from = self.request.get('came_from', None)
            if came_from:
                url += '?came_from={0:s}'.format(parse.quote(came_from))
        else:
            url = '{0:s}/insufficient-privileges'.format(portal.absolute_url())

        self.request.response.redirect(url)


class InsufficientPrivilegesView(BrowserView):

    def request_url(self):
        return self.request.get('came_from')


class InitialLoginPasswordChange(PasswordPanel):
    template = ViewPageTemplateFile(
        'templates/initial_login_password_change.pt')

    @button.buttonAndHandler(
            _(u'label_change_password', default=u'Change Password'),
            name='reset_passwd'
        )
    def action_reset_passwd(self, action):
        super(InitialLoginPasswordChange, self).action_reset_passwd(
            self, action)
        if not action.form.widgets.errors:
            self.request.response.redirect(self.context.portal_url())


class ForcedPasswordChange(PasswordPanel):
    template = ViewPageTemplateFile(
        'templates/forced_password_change.pt')

    @button.buttonAndHandler(
            _(u'label_change_password', default=u'Change Password'),
            name='reset_passwd'
        )
    def action_reset_passwd(self, action):
        super(ForcedPasswordChange, self).action_reset_passwd(self, action)
        if not action.form.widgets.errors:
            membership_tool = getToolByName(self.context, 'portal_membership')
            member = membership_tool.getAuthenticatedMember()
            member.setProperties(must_change_password=0)
            self.request.response.redirect(self.context.portal_url())
