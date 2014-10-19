# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from email import message_from_string
from plone.login import MessageFactory as _
from plone.login.browser.login_help import template_path
from plone.login.interfaces import ILoginForm
from plone.login.interfaces import ILoginFormSchema
from plone.login.interfaces import IPloneLoginLayer
from plone.login.interfaces import IRedirectAfterLogin
from plone.registry.interfaces import IRegistry
from plone.stringinterp import Interpolator
from plone.z3cform import layout
from plone.z3cform.templates import FormTemplateFactory
from z3c.form import button
from z3c.form import field
from z3c.form import form
from z3c.form.interfaces import HIDDEN_MODE
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
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

    def updateWidgets(self):
        try:
            auth = self.context.acl_users.credentials_cookie_auth
        except:
            try:
                auth = self.context.cookie_authentication
            except:
                auth = None
        if auth:
            self.fields['ac_name'].__name__ = auth.get('name_cookie', '__ac_name')  # noqa
            self.fields['ac_password'].__name__ = auth.get('pw_cookie', '__ac_password')  # noqa
        else:
            self.fields['ac_name'].__name__ = '__ac_name'
            self.fields['ac_password'].__name__ = '__ac_password'

        super(LoginForm, self).updateWidgets(prefix='')
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

    def canRequestAccess(self):
        # 1) Does the user have permissions to request access?
        has_permission = getSecurityManager().checkPermission(
            'Plone: Request Access to Content', self.context)
        # 2) Is the site's email set up properly
        controlpanel = getMultiAdapter(
            (self.context, self.request), name='overview-controlpanel')
        can_send_email = not controlpanel.mailhost_warning()
        return has_permission and can_send_email

    def request_url(self):
        return self.request.get('came_from')


class RequestAccessView(BrowserView):

    def __call__(self):
        # Send request email
        if self.send_request_email():
            # Redirect back to insufficient privilege page.
            msg = _(u'Request sent.')
            msg_type = 'info'
        else:
            msg = _(u'Unable to send request.')
            msg_type = 'error'

        IStatusMessage(self.request).addStatusMessage(msg, type=msg_type)
        redirect_url = self.request.get('came_from')
        return self.request.response.redirect(redirect_url)

    def send_request_email(self):
        mail_text = self.compile_email_template()
        encoding = getUtility(ISiteRoot).getProperty('email_charset', 'utf-8')
        # The mail headers are not properly encoded we need to extract
        # them and let MailHost manage the encoding.
        if isinstance(mail_text, unicode):
            mail_text = mail_text.encode(encoding)
        message_obj = message_from_string(mail_text.strip())
        subject = message_obj['Subject']
        m_to = message_obj['To']
        m_from = message_obj['From']
        msg_type = message_obj.get('Content-Type', 'text/plain')
        body = message_obj.get_payload()
        host = getToolByName(self, 'MailHost')

        if not m_to or m_from:
            return False
        host.send(body,
                  m_to,
                  m_from,
                  subject=subject,
                  charset=encoding,
                  msg_type=msg_type,
                  immediate=True)

    def compile_email_template(self):
        # Send message to content owners
        interp = Interpolator(self.context)

        # Pull template from controlpanel
        registry = getUtility(IRegistry)
        email_template = registry['plone.request_access_template']
        # Parse with stringinterp
        return interp(email_template)
