# -*- coding: utf-8 -*-
from zope import schema
from zope.interface import Interface
from plone.login import MessageFactory as _


class IOAuthPlugin(Interface):
    """Marker Interface for the OAuthPlugin"""


class IOAuthProvider(Interface):
    """Marker Interface for the OAuthPlugin"""


class IOAuthProviderConfiguration(Interface):
    """OAuth registry settings aligned to RFC for OAuth 2.0"""

    client_id = schema.ASCIILine(
        title=_(u'oauth_label_client_id', default=u'Client ID'),
        description=_(u'oauth_help_client_id', default=u'The client '
                      u'identifier issued to the client during the '
                      u'registration process'),
        required=True,
    )

    client_secret = schema.ASCIILine(
        title=_(u'oauth_label_client_secret', default=u'Client Secret'),
        description=_(u'oauth_help_client_secret', default=u'The client '
                      u'MAY omit the parameter if the client secret is an '
                      u'empty string.'),
        required=True,
    )

    auth_url = schema.URI(
        title=_(u'oauth_label_auth_url', default=u'Authorize URL'),
        description=_(u'oauth_help_auth_url', default=u'The authorization '
                      u'server authenticates the resource owner (via the '
                      u'user-agent) and establishes whether the resource '
                      u'owner grants or denies the client\'s access request.'),
        required=True,
    )

    response_type = schema.URI(
        title=_(u'oauth_label_response_type', default=u'Response type'),
        description=_(u'oauth_help_response_type', default=u''),
        required=True,
    )

    grant_type = schema.URI(
        title=_(u'oauth_label_grant_type', default=u'Grant type'),
        description=_(u'oauth_help_grant_type', default=u'OAuth 2 provides '
                      u'several "grant types" for different use cases. The '
                      u'grant types allowed are: authorization_code, '
                      u'implicit, password, client_credentials.'),
        required=True,
    )

    token_url = schema.URI(
        title=_(u'oauth_label_token_url', default=u'Access token URL'),
        description=_(u'oauth_help_token_url', default=u""),
        required=True,
    )

    profile_url = schema.URI(
        title=_(u'oauth_label_profile_url', default=u'Profile URL'),
        description=_(u'oauth_help_profile_url', default=u''),
        required=True,
    )

    variable_code = schema.ASCIILine(
        title=_(u'oauth_label_variable_code', default=u'Variable code'),
        description=_(u'oauth_help_variable_code', default=u'?your_variable=code'),
        required=False,
    )

    redirect_uri = schema.ASCIILine(
        title=_(u'oauth_label_redirect_uri', default=u'redirect uri'),
        description=_(u'oauth_help_redirect_uri', default=u'?redirect_uri=yourvalue'),
        required=False,
    )

    access_token = schema.ASCIILine(
        title=_(u'oauth_label_access_token', default=u'POST access token'),
        description=_(u'oauth_help_access_token', default=u"?access_token=yourvalue"),
        required=False,
    )

    state = schema.ASCIILine(
        title=_(u'oauth_label_state', default=u'POST state'),
        description=_(u'oauth_help_state', default=u"?state=yourvalue"),
        required=False,
    )
