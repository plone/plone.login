# -*- coding: utf-8 -*-
from zope.interface import Interface
from zope import schema

from plone.login import MessageFactory as _


class LoginForm(Interface):
    login = schema.TextLine(
        title=_('Login'),
    )
    password = schema.TextLine(
        title=_('Password'),
    )
