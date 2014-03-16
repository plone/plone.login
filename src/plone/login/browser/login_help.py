# -*- coding: utf-8 -*-

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage

from plone.login import MessageFactory as _
from plone.login.interfaces import ILoginHelpForm

from plone.z3cform import layout

from z3c.form import button
from z3c.form import field
from z3c.form import form


class RequestResetPassword(form.Form):

    id = "RequestResetPassword"
    label = u""
    fields = field.Fields(ILoginHelpForm).select('reset_password')
    ignoreContext = True

    render = ViewPageTemplateFile('templates/subform_render.pt')

    @button.buttonAndHandler(_('Reset your password'), name='reset')
    def handleResetPassword(self, action):
        # TODO: Send Email with password reset url
        IStatusMessage(self.request).addStatusMessage(
            _(u'An email has been sent with instructions on how to reset your '
              u'password.'),
            'info')


class RequestUsername(form.Form):

    id = "RequestUsername"
    label = u""
    fields = field.Fields(ILoginHelpForm).select('recover_username')
    ignoreContext = True

    render = ViewPageTemplateFile('templates/subform_render.pt')

    # TODO: Add validation to the field to check that is a proper email

    @button.buttonAndHandler(_('Get your username'), name='get_username')
    def handleGetUsername(self, action):
        # TODO: Send Email with username
        IStatusMessage(self.request).addStatusMessage(
            _(u'An email has been sent with your username.'),
            'info')


class LoginHelpForm(form.EditForm):
    """ Implementation of the login help form """

    subforms = []

    id = "LoginHelpForm"
    label = _(u"Need Help?")
    description = _(u"Don't worry, I forget my password all the time.")

    ignoreContext = True

    render = ViewPageTemplateFile('templates/login_help.pt')

    def can_reset_password(self):
        # TODO: Actually check that the site allows reseting password
        return True

    def can_retrieve_username(self):
        # TODO: Actually check that the site allows retrieving the username
        return True

    def update(self):
        subforms = []
        # XXX: Not really sure how to handle the action and enctype vars
        if self.can_reset_password():
            form = RequestResetPassword(None, self.request)
            form.update()
            subforms.append(form)
        if self.can_retrieve_username():
            form = RequestUsername(None, self.request)
            form.update()
            subforms.append(form)

        self.subforms = subforms
        super(LoginHelpForm, self).update()


class LoginHelpFormView(layout.FormWrapper):
    form = LoginHelpForm
