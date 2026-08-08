"""ATProto OAuth 2.1 implementation."""

from atproto_oauth.client import OAuthClient, PromptType
from atproto_oauth.exceptions import (
    OAuthError,
    OAuthStateError,
    OAuthTokenError,
    UnsupportedAuthServerError,
)
from atproto_oauth.models import OAuthSession, OAuthState
from atproto_oauth.scopes import (
    ScopeMissingError,
    ScopePermissions,
    ScopePermissionsTransition,
    ScopesSet,
)

__all__ = [
    'OAuthClient',
    'OAuthError',
    'OAuthSession',
    'OAuthState',
    'OAuthStateError',
    'OAuthTokenError',
    'PromptType',
    'ScopeMissingError',
    'ScopePermissions',
    'ScopePermissionsTransition',
    'ScopesSet',
    'UnsupportedAuthServerError',
]
