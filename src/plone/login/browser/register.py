# -*- coding: utf-8 -*-
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from AccessControl import Unauthorized
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from plone.login import MessageFactory as _
from plone.login.interfaces import IRegisterForm
from plone.z3cform import layout
from zope.component import getMultiAdapter
from z3c.form import button
from z3c.form import field
from z3c.form import form


class RegisterForm(form.EditForm):
    """ Implementation of the registration form """

    fields = field.Fields(IRegisterForm)

    id = "RegisterForm"
    label = _(u"Sign up")
    description = _(u"Join the club.")

    ignoreContext = True

    render = ViewPageTemplateFile('templates/register.pt')

    prefix = ""

    def updateWidgets(self):

        super(RegisterForm, self).updateWidgets(prefix="")

    def updateFields(self):
        fields = field.Fields(IRegisterForm)
        portal_props = getToolByName(self.context, 'portal_properties')
        props = portal_props.site_properties
        use_email_as_login = props.getProperty('use_email_as_login')
        if use_email_as_login:
            fields.remove('username')
        super(RegisterForm, self).updateFields()

    @button.buttonAndHandler(_('Register'), name='register')
    def handleRegister(self, action):

        authenticator = getMultiAdapter((self.context, self.request),
                                        name=u"authenticator")
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
            IStatusMessage(self.request).addStatusMessage(err, type="error")
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
            _(u"You are now logged in."), "info")

        # TODO: Add way to configure the redirect
        self.request.response.redirect(self.context.absolute_url())


class RegisterFormView(layout.FormWrapper):
    form = RegisterForm
