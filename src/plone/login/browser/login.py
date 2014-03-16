# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from plone.login import MessageFactory as _
from plone.login.interfaces import ILoginForm
from plone.z3cform import layout
from zope.component import getMultiAdapter
from z3c.form import button
from z3c.form import field
from z3c.form import form
from z3c.form.interfaces import HIDDEN_MODE


class LoginForm(form.EditForm):
    """ Implementation of the login form """

    fields = field.Fields(ILoginForm)

    id = "LoginForm"
    label = _(u"Log in")
    description = _(u"Long time no see.")

    ignoreContext = True

    render = ViewPageTemplateFile('templates/login.pt')

    prefix = ""

    def updateWidgets(self):
        try:
            auth = self.context.acl_users.credentials_cookie_auth
        except:
            try:
                auth = self.context.cookie_authentication
            except:
                auth = None
        if auth:
            self.fields['ac_name'].__name__ = auth.get('name_cookie', '__ac_name')
            self.fields['ac_password'].__name__ = auth.get('pw_cookie', '__ac_password')
        else:
            self.fields['ac_name'].__name__ = '__ac_name'
            self.fields['ac_password'].__name__ = '__ac_password'

        super(LoginForm, self).updateWidgets(prefix="")
        self.widgets['came_from'].mode = HIDDEN_MODE

    @button.buttonAndHandler(_('Log in'), name='login')
    def handleLogin(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        membership_tool = getToolByName(self.context, 'portal_membership')
        if membership_tool.isAnonymousUser():
            self.request.response.expireCookie('__ac', path='/')
            email_login = getToolByName(self.context, 'portal_properties') \
                .site_properties.getProperty('use_email_as_login')
            if email_login:
                IStatusMessage(self.request).addStatusMessage(
                    _(u'Login failed. Both email address and password are case '
                      u'sensitive, check that caps lock is not enabled.'),
                    'error')
            else:
                IStatusMessage(self.request).addStatusMessage(
                    _(u'Login failed. Both login name and password are case '
                      u'sensitive, check that caps lock is not enabled.'),
                    'error')
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

        IStatusMessage(self.request).addStatusMessage(_(u"You are now logged in."),
                                                      "info")
        if data['came_from']:
            came_from = data['came_from']
        else:
            came_from = self.context.portal_url()
        self.request.response.redirect(came_from)


class LoginFormView(layout.FormWrapper):
    form = LoginForm


class RequireLoginView(BrowserView):

    def __call__(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name='plone_portal_state')
        portal = portal_state.portal()
        if portal_state.anonymous():
            return portal.restrictedTraverse('login')()
        else:
            return portal.restrictedTraverse('insufficient-privileges')()


class InsufficientPrivilegesView(BrowserView):

    def canRequestAccess(self):
        return getSecurityManager().checkPermission('Plone: Request Access to Content', self.context)

    def portal_url(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name='plone_portal_state')
        return portal_state.portal_url

class RequestAccessView(BrowserView):

    def __call__(self):
        import pdb; pdb.set_trace( )



