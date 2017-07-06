# -*- coding: utf-8 -*-
from plone.login import MessageFactory as _
from plone.theme.interfaces import IDefaultPloneLayer
from plone.z3cform.interfaces import IWrappedForm
from z3c.form.interfaces import WidgetActionExecutionError
from zope import schema
from zope.interface import Interface
from zope.interface import Invalid
from zope.interface import invariant


class IPloneLoginLayer(IDefaultPloneLayer):
    """ Marker interface for plone.login views. """


class IRedirectAfterLogin(Interface):
    """ Redirect after login adapters should provide this interface """


class ILogin(Interface):
    login = schema.TextLine(
        title=_(u'label_login', default=u'Login'),
    )

    password = schema.Password(
        title=_(u'label_password', default=u'Password'),
    )


class ILoginForm(IWrappedForm):
    """ Login form marker interface """


class ILoginFormSchema(Interface):
    """ Login form schema """

    ac_name = schema.TextLine(
        title=_(u'label_login_name', default=u'Login Name'),
        required=True,
    )

    ac_password = schema.Password(
        title=_(u'label_password', default=u'Password'),
        required=True,
    )

    came_from = schema.TextLine(
        title=u'Came From',  # not translated, hidden field
        required=False,
    )


class ILoginHelpForm(IWrappedForm):
    """ Login Help form marker interface """


class ILoginHelpFormSchema(Interface):
    """ Login Help form schema """

    reset_password = schema.TextLine(
        title=_(u'label_pwreset_username', default=u'Username'),
        description=_(u'help_pwreset_username', default=u'Enter your username '
                      u'or email and we’ll send you a password reset link.'),
        required=False,
    )

    recover_username = schema.TextLine(
        title=_(u'label_pwreset_email', default=u'Email'),
        description=_(u'help_pwreset_email', default=u'Enter your email and '
                      u'we’ll send you your username.'),
        required=False,
    )


class IResetPasswordForm(IWrappedForm):
    """ reset passwort form marker interface """


class IResetPasswordFormSchema(Interface):
    """ reset password form schema """

    password = schema.Password(
        title=_(u'label_pwreset_password', default=u'Password'),
        required=True,
    )

    password_confirm = schema.Password(
        title=_(u'label_pwreset_confirm', default=u'Confirm password'),
        required=True,
    )

    @invariant
    def ensureValidPassword(obj):
        if obj.password != obj.password_confirm:
            raise WidgetActionExecutionError('password', Invalid(_(
                u'error_password_and_confirm_not_match', default=u'Password '
                u'and Confirm password do not match.')))
