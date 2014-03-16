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
