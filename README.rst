Build Status
------------

.. image:: https://travis-ci.org/plone/plone.login.svg?branch=master
    :target: https://travis-ci.org/plone/plone.login

plone.login
===========

Updating Plone's login framework 1 mockup at a time

Customize templates
-------------------

The templates for any ``plone.login`` from may be customized because they're
based on ``plone.z3cform.templates.FormTemplateFactory``.  This allows users
to customize the templates on their own themelayer without customizing form
and formwrapper classes and reregister them through zcml. Example::

    # -*- coding: utf-8 -*-
    from plone.login.interfaces import ILoginForm
    from plone.z3cform.templates import FormTemplateFactory
    from your.theme.interfaces import IYourThemeLayer

    loginform_templatefactory = FormTemplateFactory(
        template_path('/path/to/your/login_form.pt'),
        form=ILoginForm,
        request=IYourThemeLayer
    )

Then register the adapter through ZCML::

    <adapter factory=".templates.loginform_templatefactory" />


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
