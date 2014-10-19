# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from plone import api
from plone.login import MessageFactory as _
from plone.login.browser.login_help import append_klasses
from plone.login.browser.login_help import template_path
from plone.login.interfaces import IPloneLoginLayer
from plone.login.interfaces import IResetPasswordForm
from plone.login.interfaces import IResetPasswordFormSchema
from plone.z3cform import layout
from plone.z3cform.templates import FormTemplateFactory
from z3c.form import button
from z3c.form import field
from z3c.form import form
from z3c.form.interfaces import WidgetActionExecutionError
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface.exceptions import Invalid


@implementer(IResetPasswordForm)
class ResetPasswordForm(form.EditForm):
    """ Implementation of the reset password form """

    fields = field.Fields(IResetPasswordFormSchema)

    id = 'ResetPasswordForm'
    label = _(u'heading_password_reset_form', default=u'Reset password')
    description = _(u'description_password_reset_form', default=u'Reset')

    ignoreContext = True

    prefix = ''

    def updateWidgets(self):
        super(ResetPasswordForm, self).updateWidgets(prefix='')

        for idx, fn in enumerate(['password', 'password_confirm', ]):
            self.widgets[fn].tabindex = idx + 1
            append_klasses(self.widgets[fn], 'stretch')

        self.widgets['password'].placeholder = _(
            u'placeholder_password', default=u'Super secure password')

        self.widgets['password_confirm'].placeholder = _(
            u'placeholder_password_confirm', default=u'Confirm password')

    @button.buttonAndHandler(
        _(u'button_reset_password', default=u'Reset Password'),
        name='reset_password')
    def handlePasswordReset(self, action):

        authenticator = getMultiAdapter(
            (self.context, self.request), name=u'authenticator')
        if not authenticator.verify():
            raise Unauthorized
        data, errors = self.extractData()

        if errors:
            self.status = self.formErrorsMessage
            return

        if 'password' in data and 'password_confirm' in data:
            if data['password'] != data['password_confirm']:
                raise WidgetActionExecutionError('password', Invalid(_(
                    u'error_passwords_must_match', default=u'Passwords must '
                    u'match.')))

        current = api.user.get_current()

        # Try traverse subpath first:
        try:
            key = self.request['TraversalRequestNameStack'][:0]
        except IndexError:
            key = None

        # Fall back to request variable for BW compat
        if not key:
            key = self.request.get('key', None)

        pw_tool = getToolByName(self.context, 'portal_password_reset')
        # key is the value for arg randomstring
        pw_tool.resetPassword(current, key, data.get('password'))

        IStatusMessage(self.request).addStatusMessage(
            _(u'statusmessage_pwreset_passwort_was_reset', default=u'Your '
              u'password has been reset.'), 'info')

        self.request.response.redirect(self.context.absolute_url())


class ResetPasswordFormView(layout.FormWrapper):
    form = ResetPasswordForm


wrapped_pwreset_template = FormTemplateFactory(
    template_path('reset_password.pt'),
    form=IResetPasswordForm,
    request=IPloneLoginLayer
)
