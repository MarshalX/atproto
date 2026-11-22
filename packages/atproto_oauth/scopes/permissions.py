import re
import typing as t
from dataclasses import dataclass

from atproto_core.nsid import validate_nsid
from atproto_core.uri.space import is_did, is_record_key

from atproto_oauth.scopes._mime import is_accept, matches_any_accept
from atproto_oauth.scopes._parser import ParamSchema, Parser
from atproto_oauth.scopes._syntax import ScopeStringSyntax

_DID_PLC: t.Final = re.compile(r'did:plc:[a-z2-7]{24}')
_DID_WEB_HOST: t.Final = re.compile(r'(?:[A-Za-z0-9._-]|%[0-9A-F]{2})+')
_DID_WEB_LOCALHOST: t.Final = re.compile(r'localhost(?:%3A[0-9]+)?')
_DID_FRAGMENT: t.Final = re.compile(r"(?:[A-Za-z0-9._~!$&'()*+,;=:@/?-]|%[0-9A-Fa-f]{2})+")


def _is_atproto_did(value: str) -> bool:
    if _DID_PLC.fullmatch(value):
        return True

    if not value.startswith('did:web:'):
        return False

    host = value[len('did:web:') :]
    if not _DID_WEB_HOST.fullmatch(host):
        return False

    # a port is only allowed on localhost, and a path never
    return '%' not in host or bool(_DID_WEB_LOCALHOST.fullmatch(host))


def _is_nsid(value: str) -> bool:
    return validate_nsid(value, soft_fail=True)


def _is_nsid_or_wildcard(value: str) -> bool:
    return value == '*' or _is_nsid(value)


def _is_atproto_audience(value: str) -> bool:
    """Tell whether a value is ``*`` or a service of an account, such as ``did:web:example.com#service``."""
    return value == '*' or _is_atproto_service(value)


def _is_atproto_service(value: str) -> bool:
    did, separator, fragment = value.partition('#')
    return bool(separator) and bool(_DID_FRAGMENT.fullmatch(fragment)) and _is_atproto_did(did)


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


REPO_ACTIONS: t.Tuple[str, ...] = ('create', 'update', 'delete')
_is_repo_action = _known_values_validator(frozenset(REPO_ACTIONS))


def _normalize_collections(value: t.Sequence[str]) -> t.List[str]:
    return ['*'] if '*' in value else sorted(set(value))


def _normalize_repo_actions(value: t.Sequence[str]) -> t.List[str]:
    return [action for action in REPO_ACTIONS if action in value]


def _normalize_lxm(value: t.Sequence[str]) -> t.List[str]:
    return ['*'] if len(value) > 1 and '*' in value else sorted(set(value))


_repo_parser = Parser(
    'repo',
    {
        'collection': ParamSchema(
            multiple=True,
            required=True,
            validate=_is_nsid_or_wildcard,
            normalize=_normalize_collections,
        ),
        'action': ParamSchema(
            multiple=True,
            required=False,
            validate=_is_repo_action,
            default=list(REPO_ACTIONS),
            normalize=_normalize_repo_actions,
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


_DEFAULT_ACCEPT: t.Final = ('*/*',)


def _normalize_accept(value: t.Sequence[str]) -> t.List[str]:
    if '*/*' in value:
        return list(_DEFAULT_ACCEPT)

    # duplicates are kept here and dropped when the scope is formatted, which decides its form
    return sorted(_filter_non_redundant(item.lower() for item in value))


_blob_parser = Parser(
    'blob',
    {
        'accept': ParamSchema(
            multiple=True,
            required=True,
            validate=is_accept,
            normalize=_normalize_accept,
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


_rpc_parser = Parser(
    'rpc',
    {
        'lxm': ParamSchema(
            multiple=True,
            required=True,
            validate=_is_nsid_or_wildcard,
            normalize=_normalize_lxm,
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


SPACE_ACTIONS: t.Tuple[str, ...] = ('read_self', 'read', 'create', 'update', 'delete')
SPACE_MANAGE_OPERATIONS: t.Tuple[str, ...] = ('create', 'update', 'delete')

# read already implies read_self
_SPACE_DEFAULT_ACTIONS: t.Final = ('read', 'create', 'update', 'delete')
_SPACE_READ_ACTIONS: t.Final = ('read_self', 'read')


def _is_space_authority(value: str) -> bool:
    return value in ('*', 'self') or is_did(value)


def _is_space_key(value: str) -> bool:
    return value == '*' or is_record_key(value)


def _normalize_space_actions(value: t.Sequence[str]) -> t.List[str]:
    return [action for action in SPACE_ACTIONS if action in value]


def _normalize_space_manage_operations(value: t.Sequence[str]) -> t.List[str]:
    return [operation for operation in SPACE_MANAGE_OPERATIONS if operation in value]


_space_parser = Parser(
    'space',
    {
        'spaceType': ParamSchema(
            multiple=False,
            required=True,
            validate=_is_nsid_or_wildcard,
        ),
        'authority': ParamSchema(
            multiple=False,
            required=False,
            validate=_is_space_authority,
            default='self',
        ),
        'skey': ParamSchema(
            multiple=False,
            required=False,
            validate=_is_space_key,
            default='*',
        ),
        'collection': ParamSchema(
            multiple=True,
            required=False,
            validate=_is_nsid_or_wildcard,
            normalize=_normalize_collections,
        ),
        'action': ParamSchema(
            multiple=True,
            required=False,
            validate=_known_values_validator(frozenset(SPACE_ACTIONS)),
            default=list(_SPACE_DEFAULT_ACTIONS),
            normalize=_normalize_space_actions,
        ),
        'manage': ParamSchema(
            multiple=True,
            required=False,
            validate=_known_values_validator(frozenset(SPACE_MANAGE_OPERATIONS)),
            normalize=_normalize_space_manage_operations,
        ),
    },
    positional_name='spaceType',
)


@dataclass(frozen=True)
class SpacePermission:
    """Permission for operations on spaces and their records."""

    space_type: str
    authority: str
    skey: str
    collection: t.Optional[t.Tuple[str, ...]]
    action: t.Tuple[str, ...]
    manage: t.Optional[t.Tuple[str, ...]]

    def matches(
        self,
        space_type: str,
        authority: str,
        skey: str,
        action: t.Optional[str] = None,
        collection: t.Optional[str] = None,
        manage: t.Optional[str] = None,
    ) -> bool:
        if self.space_type not in ('*', space_type) or self.skey not in ('*', skey):
            return False

        # an authority of self matches nothing, as the authority of a space is always a DID
        if self.authority not in ('*', authority):
            return False

        if action is None:
            return self.manage is not None and manage in self.manage

        # reads do not depend on the collection
        if action in _SPACE_READ_ACTIONS:
            return 'read' in self.action or action in self.action

        return (
            action in self.action
            and self.collection is not None
            and ('*' in self.collection or collection in self.collection)
        )

    def __str__(self) -> str:
        values: t.Dict[str, t.Any] = {
            'spaceType': self.space_type,
            'authority': self.authority,
            'skey': self.skey,
            'action': list(self.action),
        }
        if self.collection is not None:
            values['collection'] = list(self.collection)
        if self.manage is not None:
            values['manage'] = list(self.manage)

        return _space_parser.format(values)

    @classmethod
    def from_string(cls, scope: str) -> t.Optional['SpacePermission']:
        if not _is_scope_string_for(scope, 'space'):
            return None

        syntax = ScopeStringSyntax.from_string(scope)
        return cls.from_syntax(syntax)

    @classmethod
    def from_syntax(cls, syntax: ScopeStringSyntax) -> t.Optional['SpacePermission']:
        result = _space_parser.parse(syntax)
        if result is None:
            return None

        collection = result['collection']
        manage = result['manage']

        return cls(
            space_type=result['spaceType'],
            authority=result['authority'],
            skey=result['skey'],
            collection=None if collection is None else tuple(collection),
            action=tuple(result['action']),
            manage=None if manage is None else tuple(manage),
        )

    @staticmethod
    def scope_needed_for(
        space_type: str,
        authority: str,
        skey: str,
        action: t.Optional[str] = None,
        collection: t.Optional[str] = None,
        manage: t.Optional[str] = None,
    ) -> str:
        values: t.Dict[str, t.Any] = {'spaceType': space_type, 'authority': authority, 'skey': skey}
        if manage is not None:
            # the narrowest action, so that no broader permission is suggested
            values['action'] = ['read_self']
            values['manage'] = [manage]
        else:
            values['action'] = [action]
            if action not in _SPACE_READ_ACTIONS:
                values['collection'] = [collection]

        return _space_parser.format(values)


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
            validate=_is_atproto_service,
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
