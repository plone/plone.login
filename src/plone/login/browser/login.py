from plone.login.interfaces import ILogin
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView

from z3c.form import form
from z3c.form import field


class LoginView(BrowserView):
    pass

class RegisterView(BrowserView):
    pass


class InsufficientPrivilegesView(BrowserView):
    pass


class ResetPasswordView(BrowserView):
    pass


class ForgotPasswordView(BrowserView):
    pass
