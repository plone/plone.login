from Products.Five.browser import BrowserView
from zope.interface import implements, Interface
from zope.component import getMultiAdapter
from Products.statusmessages.interfaces import IStatusMessage
from plone.login import MessageFactory as _
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import transaction_note


class ILoggedOutView(Interface):
    pass


class LogoutView(BrowserView):
    def __call__(self):
        mt = getToolByName(self.context, 'portal_membership')
        mt.logoutUser(self.request)
        transaction_note('Logged out')
        # Handle external logout requests from other portals
        next = self.request.get('next', None)
        portal_url = getToolByName(self.context, 'portal_url')
        if next is not None and portal_url.isURLInPortal(next):
            target_url = next
        else:
            target_url = self.request.URL1 + '/logged-out'

        pprops = getToolByName(self.context, 'portal_properties')
        site_properties = pprops.site_properties
        external_logout_url = site_properties.getProperty('external_logout_url')
        if external_logout_url:
            target_url = "%s?next=%s" % (external_logout_url, target_url)

        # Double '$' to avoid injection into TALES
        target_url = target_url.replace('$', '$$')
        self.request.response.redirect(target_url)


class LoggedOutView(BrowserView):

    implements(ILoggedOutView)

    def __call__(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name='plone_portal_state')
        if portal_state.anonymous():
            IStatusMessage(self.request).addStatusMessage(_(u'You have been logged out.'), 'info')
            self.request.response.redirect(
                portal_state.navigation_root_url())
        else:
            return self.index()
