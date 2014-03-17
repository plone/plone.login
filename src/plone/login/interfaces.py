# -*- coding: utf-8 -*-
from zope.interface import Interface
from zope import schema

from plone.theme.interfaces import IDefaultPloneLayer

from plone.login import MessageFactory as _


class IPloneLoginLayer(IDefaultPloneLayer):
    """ Marker interface for plone.login views. """


class ILogin(Interface):
    login = schema.TextLine(
        title=_('Login'),
    )
    password = schema.Password(
        title=_('Password'),
    )


class ICompleteProfile(Interface):
    """ Temporary schema used in the complete-profile view """

    first_name = schema.TextLine(
        title=_(u'First Name'),
        description=_(u'Please provide your first name.'),
        required=True,
    )

    last_name = schema.TextLine(
        title=_(u'Last Name'),
        description=_(u'Please provide your last name.'),
        required=True,
    )

    bio = schema.Text(
        title=_(u'Bio'),
        description=_(u'Please provide a bio of yourself.'),
        required=False,
    )


class ILoginForm(Interface):
    """ Login form schema """

    ac_name = schema.TextLine(
        title=_(u'Login Name'),
        required=True,
    )

    ac_password = schema.Password(
        title=_(u'Password'),
        required=True,
    )

    came_from = schema.TextLine(
        title=_(u'Came From'),
        required=False,
    )


class IRegisterForm(Interface):
    """ Register form schema """

    username = schema.TextLine(
        title=_(u'Username'),
        required=True,
    )

    email = schema.TextLine(
        title=_(u'Email'),
        required=True,
    )

    password = schema.Password(
        title=_(u'Password'),
        required=True,
    )

    password_ctl = schema.Password(
        title=_(u'Confirm password'),
        required=True,
    )


class ILoginHelpForm(Interface):
    """ Login Help form schema """

    reset_password = schema.TextLine(
        title=_(u'Username'),
        description=_(u'Enter your username or email and we’ll send you a '
                      u'password reset link.'),
        required=False,
    )

    recover_username = schema.TextLine(
        title=_(u'Email'),
        description=_(u'Enter your email and we’ll send you your username.'),
        required=False,
    )


class ILoginSettings(Interface):
    """ Site settings for handling user registration and authentication
    """

    request_access_template = schema.Text(
        title=_(u'Request access template'),
        description=_(u'Email sent to content owners when a user requests access.'),
        required=True,
        default=_(u"""
From: "${user_fullname}" <${user_email}>
To: ${owner_emails}, ${manager_emails}
Subject: ${user_fullname} is requesting access to ${title}

${user_fullname} is requesting access to the page "${title}" at ${url}. Please visit the sharing controls at ${url}/@@sharing to the user with username ${user_id}.""")
    )
