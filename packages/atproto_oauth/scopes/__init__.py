"""ATProto OAuth scope parsing and permission checking.

Provides spec-compliant parsing of ATProto OAuth scope strings per
the ATProto permissions specification.
"""

from atproto_oauth.scopes.exceptions import ScopeMissingError
from atproto_oauth.scopes.permissions import (
    AccountPermission,
    BlobPermission,
    IdentityPermission,
    IncludeScope,
    RepoPermission,
    RpcPermission,
)
from atproto_oauth.scopes.scope_permissions import ScopePermissions
from atproto_oauth.scopes.scopes_set import ScopesSet
from atproto_oauth.scopes.transition import ScopePermissionsTransition

__all__ = [
    'AccountPermission',
    'BlobPermission',
    'IdentityPermission',
    'IncludeScope',
    'RepoPermission',
    'RpcPermission',
    'ScopeMissingError',
    'ScopePermissions',
    'ScopePermissionsTransition',
    'ScopesSet',
]
