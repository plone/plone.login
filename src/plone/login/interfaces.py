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
    password = schema.TextLine(
        title=_('Password'),
    )


