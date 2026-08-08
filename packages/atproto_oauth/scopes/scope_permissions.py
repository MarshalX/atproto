"""Typed facade for scope permission checking."""

import typing as t

from atproto_oauth.scopes.exceptions import ScopeMissingError
from atproto_oauth.scopes.permissions import (
    AccountPermission,
    BlobPermission,
    IdentityPermission,
    RepoPermission,
    RpcPermission,
)
from atproto_oauth.scopes.scopes_set import ScopesSet


class ScopePermissions:
    """Typed permission checker wrapping a :class:`ScopesSet`.

    Example::

        perms = ScopePermissions("atproto repo:fm.plyr.track blob:*/*")
        perms.allows_repo(collection='fm.plyr.track', action='create')  # True
    """

    def __init__(self, scope: t.Optional[str] = None) -> None:
        self.scopes = ScopesSet.from_string(scope)

    def allows_repo(self, collection: str, action: str) -> bool:
        return self.scopes.matches('repo', collection=collection, action=action)

    def assert_repo(self, collection: str, action: str) -> None:
        if not self.allows_repo(collection, action):
            raise ScopeMissingError(RepoPermission.scope_needed_for(collection, action))

    def allows_blob(self, mime: str) -> bool:
        return self.scopes.matches('blob', mime=mime)

    def assert_blob(self, mime: str) -> None:
        if not self.allows_blob(mime):
            raise ScopeMissingError(BlobPermission.scope_needed_for(mime))

    def allows_rpc(self, lxm: str, aud: str) -> bool:
        return self.scopes.matches('rpc', lxm=lxm, aud=aud)

    def assert_rpc(self, lxm: str, aud: str) -> None:
        if not self.allows_rpc(lxm, aud):
            raise ScopeMissingError(RpcPermission.scope_needed_for(lxm, aud))

    def allows_account(self, attr: str, action: str) -> bool:
        return self.scopes.matches('account', attr=attr, action=action)

    def assert_account(self, attr: str, action: str) -> None:
        if not self.allows_account(attr, action):
            raise ScopeMissingError(AccountPermission.scope_needed_for(attr, action))

    def allows_identity(self, attr: str) -> bool:
        return self.scopes.matches('identity', attr=attr)

    def assert_identity(self, attr: str) -> None:
        if not self.allows_identity(attr):
            raise ScopeMissingError(IdentityPermission.scope_needed_for(attr))
