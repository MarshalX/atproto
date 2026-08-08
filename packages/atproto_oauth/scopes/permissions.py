"""Permission types for ATProto OAuth scopes.

Provides frozen dataclasses for each of the 6 scope resource types:
``repo``, ``blob``, ``rpc``, ``account``, ``identity``, and ``include``.
"""

import re
import typing as t
from dataclasses import dataclass

from atproto_core.nsid import validate_nsid

from atproto_oauth.scopes._mime import is_accept, matches_any_accept
from atproto_oauth.scopes._parser import ParamSchema, Parser
from atproto_oauth.scopes._syntax import ScopeStringSyntax

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_DID_RE = re.compile(
    r'^did:[a-z]+:[a-zA-Z0-9._:%-]*[a-zA-Z0-9._%-]'
    r'(?:#[a-zA-Z0-9._%-]+)?$'
)


def _is_nsid(value: str) -> bool:
    """Validate an NSID using atproto_core."""
    return validate_nsid(value, soft_fail=True)


def _is_nsid_or_wildcard(value: str) -> bool:
    return value == '*' or _is_nsid(value)


def _is_atproto_audience(value: str) -> bool:
    """Validate a DID or ``did:web:host#service_id`` audience string."""
    if value == '*':
        return True
    return bool(_DID_RE.match(value))


def _known_values_validator(values: t.FrozenSet[str]) -> t.Callable[[str], bool]:
    return lambda v: v in values


def _is_scope_string_for(value: str, prefix: str) -> bool:
    """Check if a scope string starts with the given prefix."""
    if len(value) > len(prefix):
        next_char = value[len(prefix)]
        if next_char not in (':', '?'):
            return False
        return value.startswith(prefix)
    return value == prefix


# ---------------------------------------------------------------------------
# RepoPermission
# ---------------------------------------------------------------------------

REPO_ACTIONS: t.Tuple[str, ...] = ('create', 'update', 'delete')
_is_repo_action = _known_values_validator(frozenset(REPO_ACTIONS))

_repo_parser = Parser(
    'repo',
    {
        'collection': ParamSchema(
            multiple=True,
            required=True,
            validate=_is_nsid_or_wildcard,
            normalize=lambda value: (['*'] if any(v == '*' for v in value) else sorted(set(value))),
        ),
        'action': ParamSchema(
            multiple=True,
            required=False,
            validate=_is_repo_action,
            default=list(REPO_ACTIONS),
            normalize=lambda value: (
                list(REPO_ACTIONS) if set(value) == set(REPO_ACTIONS) else [a for a in REPO_ACTIONS if a in value]
            ),
        ),
    },
    positional_name='collection',
)


@dataclass(frozen=True)
class RepoPermission:
    """Permission for repository record operations."""

    collection: t.Tuple[str, ...]
    action: t.Tuple[str, ...]

    def matches(self, collection: str, action: str) -> bool:
        return action in self.action and ('*' in self.collection or collection in self.collection)

    def __str__(self) -> str:
        return _repo_parser.format({'collection': list(self.collection), 'action': list(self.action)})

    @classmethod
    def from_string(cls, scope: str) -> t.Optional['RepoPermission']:
        if not _is_scope_string_for(scope, 'repo'):
            return None
        syntax = ScopeStringSyntax.from_string(scope)
        return cls.from_syntax(syntax)

    @classmethod
    def from_syntax(cls, syntax: ScopeStringSyntax) -> t.Optional['RepoPermission']:
        result = _repo_parser.parse(syntax)
        if result is None:
            return None
        return cls(
            collection=tuple(result['collection']),
            action=tuple(result['action']),
        )

    @staticmethod
    def scope_needed_for(collection: str, action: str) -> str:
        return _repo_parser.format(
            {
                'collection': [collection],
                'action': [action],
            }
        )


# ---------------------------------------------------------------------------
# BlobPermission
# ---------------------------------------------------------------------------

_DEFAULT_ACCEPT = ('*/*',)

_blob_parser = Parser(
    'blob',
    {
        'accept': ParamSchema(
            multiple=True,
            required=True,
            validate=is_accept,
            normalize=lambda value: (
                list(_DEFAULT_ACCEPT)
                if '*/*' in value
                else sorted(set(_filter_non_redundant(v.lower() if isinstance(v, str) else v for v in value)))
            ),
        ),
    },
    positional_name='accept',
)


def _filter_non_redundant(values: t.Iterable[str]) -> t.List[str]:
    """Remove MIME types that are redundant given wildcard patterns."""
    items = list(values)
    result: t.List[str] = []
    for v in items:
        if v.endswith('/*'):
            result.append(v)
        else:
            base = v.split('/', 1)[0]
            if f'{base}/*' not in items:
                result.append(v)
    return result


@dataclass(frozen=True)
class BlobPermission:
    """Permission for blob uploads."""

    accept: t.Tuple[str, ...]

    def matches(self, mime: str) -> bool:
        return matches_any_accept(self.accept, mime)

    def __str__(self) -> str:
        return _blob_parser.format({'accept': list(self.accept)})

    @classmethod
    def from_string(cls, scope: str) -> t.Optional['BlobPermission']:
        if not _is_scope_string_for(scope, 'blob'):
            return None
        syntax = ScopeStringSyntax.from_string(scope)
        return cls.from_syntax(syntax)

    @classmethod
    def from_syntax(cls, syntax: ScopeStringSyntax) -> t.Optional['BlobPermission']:
        result = _blob_parser.parse(syntax)
        if result is None:
            return None
        return cls(accept=tuple(result['accept']))

    @staticmethod
    def scope_needed_for(mime: str) -> str:
        return _blob_parser.format({'accept': [mime]})


# ---------------------------------------------------------------------------
# RpcPermission
# ---------------------------------------------------------------------------

_rpc_parser = Parser(
    'rpc',
    {
        'lxm': ParamSchema(
            multiple=True,
            required=True,
            validate=_is_nsid_or_wildcard,
            normalize=lambda value: (['*'] if len(value) > 1 and '*' in value else sorted(set(value))),
        ),
        'aud': ParamSchema(
            multiple=False,
            required=True,
            validate=_is_atproto_audience,
        ),
    },
    positional_name='lxm',
)


@dataclass(frozen=True)
class RpcPermission:
    """Permission for RPC (XRPC) method calls."""

    aud: str
    lxm: t.Tuple[str, ...]

    def matches(self, lxm: str, aud: str) -> bool:
        return (self.aud == '*' or self.aud == aud) and ('*' in self.lxm or lxm in self.lxm)

    def __str__(self) -> str:
        return _rpc_parser.format({'lxm': list(self.lxm), 'aud': self.aud})

    @classmethod
    def from_string(cls, scope: str) -> t.Optional['RpcPermission']:
        if not _is_scope_string_for(scope, 'rpc'):
            return None
        syntax = ScopeStringSyntax.from_string(scope)
        return cls.from_syntax(syntax)

    @classmethod
    def from_syntax(cls, syntax: ScopeStringSyntax) -> t.Optional['RpcPermission']:
        result = _rpc_parser.parse(syntax)
        if result is None:
            return None
        # rpc:*?aud=* is forbidden (too broad)
        if result['aud'] == '*' and '*' in result['lxm']:
            return None
        return cls(aud=result['aud'], lxm=tuple(result['lxm']))

    @staticmethod
    def scope_needed_for(lxm: str, aud: str) -> str:
        return _rpc_parser.format({'lxm': [lxm], 'aud': aud})


# ---------------------------------------------------------------------------
# AccountPermission
# ---------------------------------------------------------------------------

ACCOUNT_ATTRIBUTES: t.Tuple[str, ...] = ('email', 'repo', 'status')
ACCOUNT_ACTIONS: t.Tuple[str, ...] = ('read', 'manage')

_account_parser = Parser(
    'account',
    {
        'attr': ParamSchema(
            multiple=False,
            required=True,
            validate=_known_values_validator(frozenset(ACCOUNT_ATTRIBUTES)),
        ),
        'action': ParamSchema(
            multiple=True,
            required=False,
            validate=_known_values_validator(frozenset(ACCOUNT_ACTIONS)),
            default=['read'],
        ),
    },
    positional_name='attr',
)


@dataclass(frozen=True)
class AccountPermission:
    """Permission for account attribute access."""

    attr: str
    action: t.Tuple[str, ...]

    def matches(self, attr: str, action: str) -> bool:
        return self.attr == attr and ('manage' in self.action or action in self.action)

    def __str__(self) -> str:
        return _account_parser.format({'attr': self.attr, 'action': list(self.action)})

    @classmethod
    def from_string(cls, scope: str) -> t.Optional['AccountPermission']:
        if not _is_scope_string_for(scope, 'account'):
            return None
        syntax = ScopeStringSyntax.from_string(scope)
        return cls.from_syntax(syntax)

    @classmethod
    def from_syntax(cls, syntax: ScopeStringSyntax) -> t.Optional['AccountPermission']:
        result = _account_parser.parse(syntax)
        if result is None:
            return None
        return cls(attr=result['attr'], action=tuple(result['action']))

    @staticmethod
    def scope_needed_for(attr: str, action: str) -> str:
        return _account_parser.format({'attr': attr, 'action': [action]})


# ---------------------------------------------------------------------------
# IdentityPermission
# ---------------------------------------------------------------------------

IDENTITY_ATTRIBUTES: t.Tuple[str, ...] = ('handle', '*')

_identity_parser = Parser(
    'identity',
    {
        'attr': ParamSchema(
            multiple=False,
            required=True,
            validate=_known_values_validator(frozenset(IDENTITY_ATTRIBUTES)),
        ),
    },
    positional_name='attr',
)


@dataclass(frozen=True)
class IdentityPermission:
    """Permission for identity operations."""

    attr: str

    def matches(self, attr: str) -> bool:
        return self.attr == '*' or self.attr == attr

    def __str__(self) -> str:
        return _identity_parser.format({'attr': self.attr})

    @classmethod
    def from_string(cls, scope: str) -> t.Optional['IdentityPermission']:
        if not _is_scope_string_for(scope, 'identity'):
            return None
        syntax = ScopeStringSyntax.from_string(scope)
        return cls.from_syntax(syntax)

    @classmethod
    def from_syntax(cls, syntax: ScopeStringSyntax) -> t.Optional['IdentityPermission']:
        result = _identity_parser.parse(syntax)
        if result is None:
            return None
        return cls(attr=result['attr'])

    @staticmethod
    def scope_needed_for(attr: str) -> str:
        return _identity_parser.format({'attr': attr})


# ---------------------------------------------------------------------------
# IncludeScope
# ---------------------------------------------------------------------------

_include_parser = Parser(
    'include',
    {
        'nsid': ParamSchema(
            multiple=False,
            required=True,
            validate=_is_nsid,
        ),
        'aud': ParamSchema(
            multiple=False,
            required=False,
            validate=_is_atproto_audience,
        ),
    },
    positional_name='nsid',
)


@dataclass(frozen=True)
class IncludeScope:
    """An ``include:`` scope that references a lexicon permission set.

    Not a permission itself — it resolves via a lexicon definition to produce
    :class:`RepoPermission` and/or :class:`RpcPermission` instances.
    """

    nsid: str
    aud: t.Optional[str] = None

    def __str__(self) -> str:
        values: t.Dict[str, t.Any] = {'nsid': self.nsid}
        if self.aud is not None:
            values['aud'] = self.aud
        return _include_parser.format(values)

    def is_parent_authority_of(self, other_nsid: str) -> bool:
        """Check if ``other_nsid`` is in the same namespace authority.

        The namespace authority is everything before the last ``.`` segment of
        ``self.nsid``.  ``other_nsid`` must start with that same prefix.
        """
        if other_nsid == '*':
            return False

        group_prefix_end = self.nsid.rfind('.')
        if group_prefix_end == -1:
            raise TypeError('Dot character (".") missing from lexicon NSID')

        if group_prefix_end >= len(other_nsid) - 1:
            return False

        # Compare char-by-char up to and including the dot
        return self.nsid[: group_prefix_end + 1] == other_nsid[: group_prefix_end + 1]

    @classmethod
    def from_string(cls, scope: str) -> t.Optional['IncludeScope']:
        if not _is_scope_string_for(scope, 'include'):
            return None
        syntax = ScopeStringSyntax.from_string(scope)
        return cls.from_syntax(syntax)

    @classmethod
    def from_syntax(cls, syntax: ScopeStringSyntax) -> t.Optional['IncludeScope']:
        result = _include_parser.parse(syntax)
        if result is None:
            return None
        return cls(nsid=result['nsid'], aud=result.get('aud'))
