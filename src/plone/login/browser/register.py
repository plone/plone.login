# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from plone.login import MessageFactory as _
from plone.login.browser.login_help import append_klasses
from plone.login.browser.login_help import template_path
from plone.login.interfaces import IPloneLoginLayer
from plone.login.interfaces import IRegisterForm
from plone.login.interfaces import IRegisterFormSchema
from plone.z3cform import layout
from plone.z3cform.templates import FormTemplateFactory
from z3c.form import button
from z3c.form import field
from z3c.form import form
from zope.component import getMultiAdapter
from zope.interface import implementer


@implementer(IRegisterForm)
class RegisterForm(form.EditForm):
    ''' Implementation of the registration form '''

    fields = field.Fields(IRegisterFormSchema)

    id = 'RegisterForm'
    label = _(u'heading_register_form', default=u'Sign up')
    description = _(u'description_register_form', default=u'Join the club.')

    ignoreContext = True

    prefix = ''

    def updateWidgets(self):
        super(RegisterForm, self).updateWidgets(prefix='')
        portal_props = getToolByName(self.context, 'portal_properties')
        props = portal_props.site_properties
        use_email_as_login = props.getProperty('use_email_as_login')

        self.widgets['email'].tabindex = 1
        self.widgets['email'].autocapitalize = 'off'
        self.widgets['email'].placeholder = _(
            u'placeholder_email', default=u'Email address')
        append_klasses(self.widgets['email'], 'stretch')

        if not use_email_as_login:
            self.widgets['email'].tabindex += 1

            self.widgets['username'].tabindex = 1
            self.widgets['username'].autocapitalize = _(u'off')
            self.widgets['username'].placeholder = _(
                u'placeholder_username', default=u'Username')
            append_klasses(self.widgets['username'], 'stretch')

        self.widgets['password'].tabindex = 3
        self.widgets['password'].placeholder = _(
            u'placeholder_password', default=u'Super secure password')
        append_klasses(self.widgets['password'], 'stretch')

        self.widgets['password_confirm'].tabindex = 4
        self.widgets['password_confirm'].placeholder = _(
            u'placeholder_password_confirm', default=u'Confirm password')
        append_klasses(self.widgets['password_confirm'], 'stretch')

    def updateFields(self):
        super(RegisterForm, self).updateFields()
        fields = field.Fields(IRegisterForm)
        portal_props = getToolByName(self.context, 'portal_properties')
        props = portal_props.site_properties
        use_email_as_login = props.getProperty('use_email_as_login')
        if use_email_as_login:
            fields.remove('username')

    @button.buttonAndHandler(
        _(u'button_register', default=u'Register'), name='register')
    def handleRegister(self, action):

        authenticator = getMultiAdapter((self.context, self.request),
                                        name=u'authenticator')
        if not authenticator.verify():
            raise Unauthorized
        data, errors = self.extractData()

        if errors:
            self.status = self.formErrorsMessage
            return

        password = str(data.get('password'))
        username = str(data.get('username'))
        email = data.get('email')

        portal_props = getToolByName(self.context, 'portal_properties')
        props = portal_props.site_properties
        use_email_as_login = props.getProperty('use_email_as_login')
        if use_email_as_login:
            username = email = str(data.get('email'))

        registration = getToolByName(self.context, 'portal_registration')
        try:
            registration.addMember(username, password)
        except (AttributeError, ValueError), err:
            IStatusMessage(self.request).addStatusMessage(err, type='error')
            return

        authenticated = self.context.acl_users.authenticate(username,
                                                            password,
                                                            self.request)
        if authenticated:
            self.context.acl_users.updateCredentials(self.request,
                                                     self.request.response,
                                                     username,
                                                     password)

        membership_tool = getToolByName(self.context, 'portal_membership')
        member = membership_tool.getMemberById(username)

        # XXX: Improve this for further fields
        member.setMemberProperties({'email': email})

        login_time = member.getProperty('login_time', '2000/01/01')
        if not isinstance(login_time, DateTime):
            login_time = DateTime(login_time)
        initial_login = login_time == DateTime('2000/01/01')
        if initial_login:
            # TODO: Redirect if this is initial login
            pass

        IStatusMessage(self.request).addStatusMessage(
            _(u'statusmessage_your_now_logged_in', default=u'You are now '
              u'logged in.'), 'info')

        # TODO: Add way to configure the redirect
        self.request.response.redirect(self.context.absolute_url())


class RegisterFormView(layout.FormWrapper):
    form = RegisterForm


wrapped_register_template = FormTemplateFactory(
    template_path('register.pt'),
    form=IRegisterForm,
    request=IPloneLoginLayer
)
