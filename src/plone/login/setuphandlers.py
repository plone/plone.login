# -*- coding: utf-8 -*-
from plone.login.auth.plugin import OAuthPlugin


def skip_if_not_this_profile(fun):
    def decorator(context):
        if not context.readDataFile('is_plone_login_profile.txt'):
            return
        fun(context)
    return decorator


def addOAuthPlugin(pas, plugin_id='pas-oauth', plugin_title='OAuth plugin'):
    if plugin_id in pas.objectIds():
        return '{0:s} already installed.'.format(plugin_title)

    plugin = OAuthPlugin(plugin_id, title=plugin_title)
    pas._setObject(plugin_id, plugin)
    plugin = pas[plugin.getId()]  # get plugin acquisition wrapped!
    for info in pas.plugins.listPluginTypeInfo():
        interface = info['interface']
        if not interface.providedBy(plugin):
            continue
        pas.plugins.activatePlugin(interface, plugin.getId())
        pas.plugins.movePluginsDown(
            interface,
            [x[0] for x in pas.plugins.listPlugins(interface)[:-1]],
        )


@skip_if_not_this_profile
def setupPlugins(context):
    site = context.getSite()
    addOAuthPlugin(site.acl_users)
