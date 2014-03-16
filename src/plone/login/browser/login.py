# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage

from plone.login import MessageFactory as _
from plone.login.interfaces import ILoginForm

from plone.z3cform import layout

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

    def updateWidgets(self):
        super(LoginForm, self).updateWidgets()
        self.widgets['came_from'].mode = HIDDEN_MODE

    @button.buttonAndHandler(_('Log in'), name='login')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        #self.applyChanges(data)
        # XXX: NEED TO LOGIN NOW
        IStatusMessage(self.request).addStatusMessage(_(u"You're now logged in."),
                                                      "info")

class LoginFormView(layout.FormWrapper):
    form = LoginForm
