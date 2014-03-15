from Products.Five.browser import BrowserView


class LoginView(BrowserView):
    pass


class RegisterView(BrowserView):
    pass

class ConfirmationSentView(BrowserView):
    pass    

class InsufficientPrivilegesView(BrowserView):
    pass


class ResetPasswordView(BrowserView):
    pass


class SendEmailView(BrowserView):
    pass


class LoginHelpView(BrowserView):

    def can_reset_password(self):
        return True

    def can_retrieve_username(self):
        return True
