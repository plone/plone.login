.. contents::

plone.login
===========

Updating Plone's login framework 1 mockup at a time

Customize where to redirect after login
---------------------------------------

You can customize the location the user will be redirected to after successfuly
logging in to the site.

Just write an adapter as follows::

    from zope.interface import implements
    from plone.login.interfaces import IRedirectAfterLogin
    ...
    ...
    ...
    class AfterLoginAdapter(object):

        implements(IRedirectAfterLogin)

        def __init__(self, context, request):
            self.context = context
            self.request = request

        def __call__(self, came_from=None):
            # Your logic here
            return "http://plone.org"


Then register the adapter through ZCML::

    <adapter
        factory=".adapter.AfterLoginAdapter"
        for="OFS.interfaces.ITraversable
             zope.publisher.interfaces.IRequest"
        />


As you can see, this adapter adapts context and request, so modify these
according to your needs.
