Build Status
------------

.. image:: https://travis-ci.org/plone/plone.login.svg?branch=master
    :target: https://travis-ci.org/plone/plone.login

.. image:: https://coveralls.io/repos/github/plone/plone.login/badge.svg?branch=master
    :target: https://coveralls.io/github/plone/plone.login?branch=master


plone.login
===========

A modernized drop-in replacement for the portal_skins-based login.


Installation
------------

Install ploneconf.site by adding it to your buildout::

    [buildout]

    ...

    eggs =
        plone.login

and then running ``bin/buildout``. Install it as usual in /prefs_install_products_form


Compatibility
-------------

``plone.login`` is tested to work with Plone 5.1.
It should work with Plone 5.0 as well but is not yet tested.


Customizing templates
---------------------

The templates for any ``plone.login`` can be customized because they're simple browser-views.
Use `z3c.jbot <https://pypi.org/project/z3c.jbot/>`_ to apply your own overides.

Customize where to redirect after login
---------------------------------------

You can customize the location the user will be redirected to after successfuly logging in to the site.

Just write an adapter as follows

..  code-block:: python

    from plone.login.interfaces import IRedirectAfterLogin
    from plone.login.interfaces import IInitialLogin
    from Products.CMFPlone.utils import safe_unicode
    from zope.interface import implementer
    from plone import api


    @implementer(IRedirectAfterLogin)
    class RedirectAfterLoginAdapter(object):

        def __init__(self, context, request):
            self.context = context
            self.request = request

        def __call__(self, came_from=None, is_initial_login=False):
            if 'Reviewer' in api.user.get_roles():
                api.portal.show_message(
                    u'Get to work!', self.request)
                came_from = self.context.portal_url() + '/@@full_review_list'
            else:
                user = api.user.get_current()
                fullname = safe_unicode(user.getProperty('fullname'))
                api.portal.show_message(
                    u'Nice to see you again, {0}!'.format(fullname), self.request)
            if not came_from:
                came_from = self.context.portal_url()
            return came_from

Then register the adapter through ZCML::

    <adapter
        factory="your.addon.adapters.RedirectAfterLoginAdapter"
        for="OFS.interfaces.ITraversable
             zope.publisher.interfaces.IRequest"
        />

As you can see, this adapter adapts context and request, so modify these according to your needs.
