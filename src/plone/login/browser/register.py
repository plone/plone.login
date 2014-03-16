# -*- coding: utf-8 -*-
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from plone.login import MessageFactory as _
from plone.login.interfaces import IRegisterForm
from plone.z3cform import layout
from zope.component import getMultiAdapter
from z3c.form import button
from z3c.form import field
from z3c.form import form
from z3c.form.interfaces import HIDDEN_MODE


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

    @button.buttonAndHandler(_('Register'), name='register')
    def handleRegister(self, action):
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


class RegisterFormView(layout.FormWrapper):
    form = RegisterForm
