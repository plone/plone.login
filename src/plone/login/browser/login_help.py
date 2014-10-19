# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from plone.login import MessageFactory as _
from plone.login.interfaces import ILoginHelpForm
from plone.login.interfaces import ILoginHelpFormSchema
from plone.login.interfaces import IPloneLoginLayer
from plone.z3cform import layout
from plone.z3cform.templates import FormTemplateFactory
from z3c.form import button
from z3c.form import field
from z3c.form import form
from zope.interface import implementer
import os

template_path = lambda p: os.path.join(
    os.path.dirname(__file__), 'templates', p)


def append_klasses(widget, klasses):
    if isinstance(klasses, (basestring, unicode)):
        klasses = [klasses, ]

    klasses.insert(0, getattr(widget, 'klass', None))
    return ' '.join(filter(None, klasses))


class RequestResetPassword(form.Form):

    id = 'RequestResetPassword'
    label = u''
    fields = field.Fields(ILoginHelpFormSchema).select('reset_password')
    ignoreContext = True

    render = ViewPageTemplateFile('templates/subform_render.pt')

    @button.buttonAndHandler(
        _(u'button_pwreset_reset_password', default=u'Reset your password'),
        name='reset')
    def handleResetPassword(self, action):
        # TODO: Send Email with password reset url
        IStatusMessage(self.request).addStatusMessage(
            _(u'statusmessage_pwreset_password_mail_sent', default=u'An '
              u'email has been sent with instructions on how to reset your '
              u'password.'), 'info')


class RequestUsername(form.Form):

    id = 'RequestUsername'
    label = u''
    fields = field.Fields(ILoginHelpFormSchema).select('recover_username')
    ignoreContext = True

    render = ViewPageTemplateFile('templates/subform_render.pt')

    # TODO: Add validation to the field to check that is a proper email

    @button.buttonAndHandler(
        _(u'button_pwreset_get_username', default='Get your username'),
        name='get_username')
    def handleGetUsername(self, action):
        # TODO: Send Email with username
        IStatusMessage(self.request).addStatusMessage(
            _(u'statusmessage_pwreset_username_mail_sent', default=u'An '
              u'email has been sent with your username.'), 'info')


@implementer(ILoginHelpForm)
class LoginHelpForm(form.EditForm):
    ''' Implementation of the login help form '''

    subforms = []

    id = 'LoginHelpForm'
    label = _(u'heading_login_form_help', default=u'Need Help?')
    description = _(u'description_login_form_help', default=u'Don\'t worry, I '
                    u'forget my password all the time.')

    ignoreContext = True

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


wrapped_loginhelp_template = FormTemplateFactory(
    template_path('login_help.pt'),
    form=ILoginHelpForm,
    request=IPloneLoginLayer
)
