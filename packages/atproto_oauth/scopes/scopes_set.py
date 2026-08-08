"""ScopesSet — container for parsed OAuth scope strings."""

import typing as t

from atproto_oauth.scopes.exceptions import ScopeMissingError
from atproto_oauth.scopes.permissions import (
    AccountPermission,
    BlobPermission,
    IdentityPermission,
    RepoPermission,
    RpcPermission,
)


def _parse_permission(
    resource: str, scope: str
) -> t.Union[RepoPermission, BlobPermission, RpcPermission, AccountPermission, IdentityPermission, None]:
    """Try to parse a scope string as the given resource type."""
    if resource == 'repo':
        return RepoPermission.from_string(scope)
    if resource == 'blob':
        return BlobPermission.from_string(scope)
    if resource == 'rpc':
        return RpcPermission.from_string(scope)
    if resource == 'account':
        return AccountPermission.from_string(scope)
    if resource == 'identity':
        return IdentityPermission.from_string(scope)
    return None


def _scope_needed_for(resource: str, **kwargs: t.Any) -> str:
    """Generate the scope string needed for a permission check."""
    if resource == 'repo':
        return RepoPermission.scope_needed_for(**kwargs)
    if resource == 'blob':
        return BlobPermission.scope_needed_for(**kwargs)
    if resource == 'rpc':
        return RpcPermission.scope_needed_for(**kwargs)
    if resource == 'account':
        return AccountPermission.scope_needed_for(**kwargs)
    if resource == 'identity':
        return IdentityPermission.scope_needed_for(**kwargs)
    raise TypeError(f'Unknown resource: {resource}')


class ScopesSet:
    """A set of OAuth scope strings with permission matching.

    Example::

        scopes = ScopesSet.from_string("atproto repo:fm.plyr.track blob:*/*")
        scopes.matches('repo', collection='fm.plyr.track', action='create')  # True
        scopes.matches('blob', mime='image/png')  # True
    """

    def __init__(self, scopes: t.Optional[t.Iterable[str]] = None) -> None:
        self._scopes: t.Set[str] = set(scopes) if scopes else set()

    @classmethod
    def from_string(cls, scope_string: t.Optional[str] = None) -> 'ScopesSet':
        """Parse a space-separated scope string."""
        if not scope_string:
            return cls()
        return cls(scope_string.split())

    def has(self, scope: str) -> bool:
        """Check if an exact scope string is in the set."""
        return scope in self._scopes

    def add(self, scope: str) -> None:
        """Add a scope string to the set."""
        self._scopes.add(scope)

    def discard(self, scope: str) -> None:
        """Remove a scope string if present."""
        self._scopes.discard(scope)

    @property
    def size(self) -> int:
        return len(self._scopes)

    def matches(self, resource: str, **kwargs: t.Any) -> bool:
        """Check if any scope in the set grants the requested permission.

        Args:
            resource: The resource type (``repo``, ``blob``, ``rpc``, ``account``, ``identity``).
            **kwargs: Permission-specific parameters passed to ``matches()``.

        Returns:
            True if any scope grants the permission.
        """
        for scope in self._scopes:
            perm = _parse_permission(resource, scope)
            if perm is not None:
                type_map = {
                    'repo': RepoPermission,
                    'blob': BlobPermission,
                    'rpc': RpcPermission,
                    'account': AccountPermission,
                    'identity': IdentityPermission,
                }
                expected = type_map.get(resource)
                if expected and isinstance(perm, expected) and perm.matches(**kwargs):
                    return True
        return False

    def assert_matches(self, resource: str, **kwargs: t.Any) -> None:
        """Assert that a scope grants the requested permission.

        Raises :class:`~atproto_oauth.scopes.exceptions.ScopeMissingError` if not.
        """
        if not self.matches(resource, **kwargs):
            scope = _scope_needed_for(resource, **kwargs)
            raise ScopeMissingError(scope)

    def __iter__(self) -> t.Iterator[str]:
        return iter(self._scopes)

    def __len__(self) -> int:
        return len(self._scopes)

    def __contains__(self, item: str) -> bool:
        return item in self._scopes

    def __repr__(self) -> str:
        return f'ScopesSet({self._scopes!r})'
