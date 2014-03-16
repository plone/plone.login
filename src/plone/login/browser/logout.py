from Products.Five.browser import BrowserView
from zope.interface import implements, Interface
from zope.component import getMultiAdapter
from Products.statusmessages.interfaces import IStatusMessage
from plone.login import MessageFactory as _


class ILoggedOutView(Interface):
    pass


class LoggedOutView(BrowserView):

    implements(ILoggedOutView)

    def __call__(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name='plone_portal_state')
        if portal_state.anonymous():
            IStatusMessage(self.request).addStatusMessage(_(u'You have been \
                                                         logged out'), 'info')
            self.request.response.redirect(
                portal_state.navigation_root_url())
        else:
            return self.index()
