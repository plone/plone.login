# -*- coding: utf-8 -*-
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from plone.login import MessageFactory as _
from plone.login.interfaces import IRegisterForm
from plone.z3cform import layout
from zope.interface import Invalid
from zope.component import getMultiAdapter
from z3c.form import button
from z3c.form import field
from z3c.form import form
from z3c.form.interfaces import HIDDEN_MODE
from z3c.form.interfaces import WidgetActionExecutionError


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
        props = portal_props.site_properties
        use_email_as_login = props.getProperty('use_email_as_login')
        if use_email_as_login:
            fields.remove('username')
        super(RegisterForm, self).updateFields()



    @button.buttonAndHandler(_('Register'), name='register')
    def handleRegister(self, action):

        authenticator=getMultiAdapter((self.context, self.request),
                                      name=u"authenticator")
        if not authenticator.verify():
            raise Unauthorized

        data, errors = self.extractData()

        if 'password' in data:
            password = data.get('password')
            password_ctl = data.get('password_ctl')
            if password != password_ctl:
                    raise WidgetActionExecutionError(
                    'email',
                    Invalid(u"Passwords must match"))

        if 'username' in data:
            username = data.get('username')

        if 'email' in data:
            email = data.get('email')

        props = portal_props.site_properties
        use_email_as_login = props.getProperty('use_email_as_login')
        if use_email_as_login:
            username, email = data.get('email')

        if errors:
            self.status = self.formErrorsMessage
            return


        registration = getToolByName(self.context, 'portal_registration')
        try:
            registration.addMember(username, password, REQUEST=self.request)
        except (AttributeError, ValueError), err:
            logging.exception(err)
            IStatusMessage(self.request).addStatusMessage(err, type="error")
            return

        membership_tool = getToolByName(self.context, 'portal_membership')
        membership_tool.loginUser(self.request)
        member = membership_tool.getAuthenticatedMember()
        login_time = member.getProperty('login_time', '2000/01/01')
        if not isinstance(login_time, DateTime):
            login_time = DateTime(login_time)
        initial_login = login_time == DateTime('2000/01/01')
        if initial_login:
            # TODO: Redirect if this is initial login
            pass

        IStatusMessage(self.request).addStatusMessage(_(u"You are now logged in."),
                                                    "info")
        if data['came_from']:
            came_from = data['came_from']
        else:
            came_from = self.context.portal_url()
        self.request.response.redirect(came_from)


class RegisterFormView(layout.FormWrapper):
    form = RegisterForm
