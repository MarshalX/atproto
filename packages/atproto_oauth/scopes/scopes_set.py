import typing as t

from atproto_oauth.exceptions import ScopeMissingError
from atproto_oauth.scopes.permissions import (
    AccountPermission,
    BlobPermission,
    IdentityPermission,
    RepoPermission,
    RpcPermission,
)

_Permission = t.Union[RepoPermission, BlobPermission, RpcPermission, AccountPermission, IdentityPermission]

_PERMISSIONS: t.Final[t.Dict[str, t.Type[_Permission]]] = {
    'repo': RepoPermission,
    'blob': BlobPermission,
    'rpc': RpcPermission,
    'account': AccountPermission,
    'identity': IdentityPermission,
}


def _scope_needed_for(resource: str, **kwargs: t.Any) -> str:
    permission = _PERMISSIONS.get(resource)
    if permission is None:
        raise ValueError(f'Unknown resource type: {resource}')

    return permission.scope_needed_for(**kwargs)


class ScopesSet:
    """A set of OAuth scope strings with permission matching.

    Example::

        scopes = ScopesSet.from_string('atproto repo:com.example.record blob:*/*')
        scopes.matches('repo', collection='com.example.record', action='create')  # True
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
            :obj:`bool`: Whether any scope grants the permission.
        """
        permission = _PERMISSIONS.get(resource)
        if permission is None:
            return False

        for scope in self._scopes:
            parsed = permission.from_string(scope)
            if parsed is not None and parsed.matches(**kwargs):
                return True

        return False

    def assert_matches(self, resource: str, **kwargs: t.Any) -> None:
        """Ensure that a scope grants the requested permission.

        Raises:
            :class:`atproto_oauth.exceptions.ScopeMissingError`: No scope grants the permission.
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
