from plone.login.interfaces import ILogin
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView

from z3c.form import form
from z3c.form import field


class LoginForm(form.Form):
    field = field.Fields(ILogin)
    ignoreContext = True
    label = "Content status history dates"


class LoginView(BrowserView):
    template = ViewPageTemplateFile('templates/login.pt')

    def __init__(self, context, request):
        super(LoginView, self).__init__(context, request)

        self.login_form = LoginForm(context, request)
        self.login_form.updateWidgets()


class RegisterView(BrowserView):
    pass

class InsufficientPrivilegesView(BrowserView):
    pass


class ResetPasswordView(BrowserView):
    pass


class ForgotPasswordView(BrowserView):
    pass
