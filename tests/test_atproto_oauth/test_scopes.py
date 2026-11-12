import typing as t

import pytest
from atproto_oauth.scopes import (
    AccountPermission,
    BlobPermission,
    IdentityPermission,
    IncludeScope,
    RepoPermission,
    RpcPermission,
    ScopeMissingError,
    ScopePermissions,
    ScopePermissionsTransition,
    ScopesSet,
)
from atproto_oauth.scopes._mime import is_accept, is_mime, matches_accept, matches_any_accept
from atproto_oauth.scopes._syntax import ScopeStringSyntax


@pytest.mark.parametrize(
    ('scope', 'prefix', 'positional', 'params'),
    [
        ('my-res', 'my-res', None, {}),
        ('my-res:my-pos', 'my-res', 'my-pos', {}),
        ('my-res:', 'my-res', '', {}),
        (
            'my-res:foo?x=value&y=value-y',
            'my-res',
            'foo',
            {'x': ['value'], 'y': ['value-y']},
        ),
        (
            'my-res?x=value&y=value-y',
            'my-res',
            None,
            {'x': ['value'], 'y': ['value-y']},
        ),
        (
            'my-res?x=foo&x=bar&x=baz',
            'my-res',
            None,
            {'x': ['foo', 'bar', 'baz']},
        ),
    ],
)
def test_scope_string_syntax_parse_scope(
    scope: str,
    prefix: str,
    positional: t.Optional[str],
    params: t.Dict[str, t.List[str]],
) -> None:
    syntax = ScopeStringSyntax.from_string(scope)
    assert syntax.prefix == prefix
    assert syntax.positional == positional
    assert syntax.params == params


def test_scope_string_syntax_get_multi_returns_none_for_absent() -> None:
    syntax = ScopeStringSyntax.from_string('my-res')
    assert syntax.get_multi('nonexistent') is None


def test_scope_string_syntax_get_multi_returns_values() -> None:
    syntax = ScopeStringSyntax.from_string('my-res?x=foo&x=bar')
    assert syntax.get_multi('x') == ['foo', 'bar']


def test_scope_string_syntax_url_encoding_in_positional() -> None:
    syntax = ScopeStringSyntax.from_string('my-res:my%20pos')
    assert syntax.positional == 'my pos'


def test_scope_string_syntax_url_encoding_in_params() -> None:
    syntax = ScopeStringSyntax.from_string('my-res?x=my%20value')
    assert syntax.get_multi('x') == ['my value']


def test_scope_string_syntax_colon_in_positional() -> None:
    syntax = ScopeStringSyntax.from_string('my-res:my:pos')
    assert syntax.positional == 'my:pos'


def test_scope_string_syntax_rpc_scope_with_did_in_params() -> None:
    """DID values in params contain colons which should not be treated as positional."""
    syntax = ScopeStringSyntax.from_string('rpc:foo.bar?aud=did:foo:bar?lxm=bar.baz')
    assert syntax.prefix == 'rpc'
    assert syntax.positional == 'foo.bar'
    # parse_qs splits on & only; the inner ? is part of the value
    aud_values = syntax.get_multi('aud')
    assert aud_values == ['did:foo:bar?lxm=bar.baz']


def test_repo_permission_parse_positional() -> None:
    scope = RepoPermission.from_string('repo:com.example.foo')
    assert scope is not None
    assert scope.collection == ('com.example.foo',)
    assert scope.action == ('create', 'update', 'delete')


def test_repo_permission_parse_with_actions() -> None:
    scope = RepoPermission.from_string('repo:com.example.foo?action=create&action=update')
    assert scope is not None
    assert scope.collection == ('com.example.foo',)
    assert scope.action == ('create', 'update')


def test_repo_permission_parse_without_actions_defaults_to_all() -> None:
    scope = RepoPermission.from_string('repo:com.example.foo')
    assert scope is not None
    assert scope.action == ('create', 'update', 'delete')


def test_repo_permission_wildcard_collection_with_action() -> None:
    scope = RepoPermission.from_string('repo:*?action=create')
    assert scope is not None
    assert scope.collection == ('*',)
    assert scope.action == ('create',)
    assert scope.matches(collection='any.collection.name', action='create')
    assert not scope.matches(collection='any.collection.name', action='update')


def test_repo_permission_wildcard_collection_without_actions() -> None:
    scope = RepoPermission.from_string('repo:*')
    assert scope is not None
    assert scope.matches(collection='any.collection.name', action='create')
    assert scope.matches(collection='any.collection.name', action='update')
    assert scope.matches(collection='any.collection.name', action='delete')


@pytest.mark.parametrize(
    'invalid',
    [
        'repo:foo bar',
        'repo:.foo',
        'repo:bar.',
        'repo:*?action=*',
        'invalid',
        'repo:invalid',
        'repo:com.example.foo?action=invalid',
        'repo?collection=invalid&action=invalid',
    ],
)
def test_repo_permission_rejects_invalid(invalid: str) -> None:
    assert RepoPermission.from_string(invalid) is None


def test_repo_permission_matches_create_action() -> None:
    scope = RepoPermission.from_string('repo:com.example.foo?action=create')
    assert scope is not None
    assert scope.matches(action='create', collection='com.example.foo')


def test_repo_permission_not_matches_unspecified_action() -> None:
    scope = RepoPermission.from_string('repo:com.example.foo?action=create')
    assert scope is not None
    assert not scope.matches(action='update', collection='com.example.foo')


def test_repo_permission_matches_wildcard_collection() -> None:
    scope = RepoPermission.from_string('repo:*?action=create')
    assert scope is not None
    assert scope.matches(action='create', collection='com.example.bar')


def test_repo_permission_matches_multiple_actions() -> None:
    scope = RepoPermission.from_string('repo:com.example.foo?action=create&action=update')
    assert scope is not None
    assert scope.matches(action='create', collection='com.example.foo')
    assert scope.matches(action='update', collection='com.example.foo')
    assert not scope.matches(action='delete', collection='com.example.foo')


def test_repo_permission_scope_needed_for() -> None:
    scope = RepoPermission.scope_needed_for(collection='com.example.foo', action='create')
    assert scope == 'repo:com.example.foo?action=create'


def test_repo_permission_format() -> None:
    scope = RepoPermission(collection=('com.example.foo',), action=('create', 'update'))
    assert str(scope) == 'repo:com.example.foo?action=create&action=update'


@pytest.mark.parametrize(
    ('input_scope', 'expected'),
    [
        ('repo:com.example.foo', 'repo:com.example.foo'),
        ('repo:com.example.foo?action=create', 'repo:com.example.foo?action=create'),
        ('repo:com.example.foo?action=create&action=update', 'repo:com.example.foo?action=create&action=update'),
        ('repo:*?action=create&action=update&action=delete', 'repo:*'),
        ('repo:com.example.foo?action=create&action=update&action=delete', 'repo:com.example.foo'),
        ('repo:*?action=create', 'repo:*?action=create'),
        ('repo:*?action=update', 'repo:*?action=update'),
        ('repo?collection=*&action=update', 'repo:*?action=update'),
        ('repo?collection=*&collection=com.example.foo&action=update', 'repo:*?action=update'),
        ('repo?collection=*', 'repo:*'),
        ('repo?collection=*&action=create&action=update&action=delete', 'repo:*'),
        ('repo?collection=*&collection=com.example.foo', 'repo:*'),
        ('repo?action=create&collection=com.example.foo', 'repo:com.example.foo?action=create'),
        (
            'repo?collection=com.example.foo&action=create&action=update&action=delete',
            'repo:com.example.foo',
        ),
        (
            'repo?action=create&collection=com.example.foo&collection=com.example.bar',
            'repo?collection=com.example.bar&collection=com.example.foo&action=create',
        ),
    ],
)
def test_repo_permission_normalization_roundtrip(input_scope: str, expected: str) -> None:
    result = RepoPermission.from_string(input_scope)
    assert result is not None
    assert str(result) == expected


def test_blob_permission_parse_positional() -> None:
    scope = BlobPermission.from_string('blob:image/png')
    assert scope is not None
    assert scope.accept == ('image/png',)


def test_blob_permission_parse_multiple_accept() -> None:
    scope = BlobPermission.from_string('blob?accept=image/png&accept=image/jpeg')
    assert scope is not None
    assert set(scope.accept) == {'image/png', 'image/jpeg'}


def test_blob_permission_reject_without_accept() -> None:
    assert BlobPermission.from_string('blob') is None


@pytest.mark.parametrize(
    'invalid',
    [
        'invalid',
        'scope',
        'blob:invalid',
        'blob?accept=invalid-mime',
        'blob?accept=invalid',
        'blob:*/**',
        'blob:*/png',
    ],
)
def test_blob_permission_rejects_invalid(invalid: str) -> None:
    assert BlobPermission.from_string(invalid) is None


def test_blob_permission_matches_exact_mime() -> None:
    scope = BlobPermission.from_string('blob:image/png')
    assert scope is not None
    assert scope.matches('image/png')


def test_blob_permission_matches_wildcard_all() -> None:
    scope = BlobPermission.from_string('blob:*/*')
    assert scope is not None
    assert scope.matches('image/jpeg')
    assert scope.matches('application/json')


def test_blob_permission_matches_subtype_wildcard() -> None:
    scope = BlobPermission.from_string('blob:image/*')
    assert scope is not None
    assert scope.matches('image/gif')
    assert not scope.matches('application/json')


def test_blob_permission_not_matches_different_mime() -> None:
    scope = BlobPermission.from_string('blob:image/png')
    assert scope is not None
    assert not scope.matches('image/jpeg')


def test_blob_permission_matches_multiple_accept() -> None:
    scope = BlobPermission.from_string('blob?accept=image/png&accept=image/jpeg')
    assert scope is not None
    assert scope.matches('image/png')
    assert scope.matches('image/jpeg')
    assert not scope.matches('image/gif')


def test_blob_permission_scope_needed_for() -> None:
    assert BlobPermission.scope_needed_for('image/png') == 'blob:image/png'


def test_blob_permission_strips_redundant_accept() -> None:
    assert str(BlobPermission(accept=('*/*', 'image/*'))) == 'blob:*/*'
    assert str(BlobPermission(accept=('*/*', 'image/png'))) == 'blob:*/*'
    assert str(BlobPermission(accept=('image/*', 'image/png'))) == 'blob:image/*'


def test_blob_permission_positional_format_for_single() -> None:
    assert str(BlobPermission(accept=('image/png',))) == 'blob:image/png'
    assert str(BlobPermission(accept=('image/*',))) == 'blob:image/*'
    assert str(BlobPermission(accept=('*/*',))) == 'blob:*/*'


def test_blob_permission_query_format_for_multiple() -> None:
    result = str(BlobPermission(accept=('image/png', 'image/jpeg')))
    assert result == 'blob?accept=image/jpeg&accept=image/png'


def test_rpc_permission_parse_positional_with_aud() -> None:
    scope = RpcPermission.from_string('rpc:com.example.service?aud=did:web:example.com%23service_id')
    assert scope is not None
    assert scope.aud == 'did:web:example.com#service_id'
    assert scope.lxm == ('com.example.service',)


def test_rpc_permission_parse_query_format() -> None:
    scope = RpcPermission.from_string('rpc?lxm=com.example.method1&aud=*')
    assert scope is not None
    assert scope.aud == '*'
    assert scope.lxm == ('com.example.method1',)


def test_rpc_permission_parse_positional_equivalent() -> None:
    scope = RpcPermission.from_string('rpc:com.example.method1?aud=*')
    assert scope is not None
    assert scope.aud == '*'
    assert scope.lxm == ('com.example.method1',)


def test_rpc_permission_parse_multiple_lxm() -> None:
    scope = RpcPermission.from_string('rpc?aud=*&lxm=com.example.method1&lxm=com.example.method2')
    assert scope is not None
    assert scope.aud == '*'
    assert scope.lxm == ('com.example.method1', 'com.example.method2')


def test_rpc_permission_rejects_without_lxm() -> None:
    assert RpcPermission.from_string('rpc?aud=did:web:example.com%23service_id') is None
    assert RpcPermission.from_string('rpc:?aud=did:web:example.com%23service_id') is None


def test_rpc_permission_rejects_without_aud() -> None:
    assert RpcPermission.from_string('rpc?lxm=com.example.method1') is None
    assert RpcPermission.from_string('rpc:com.example.method1') is None


def test_rpc_permission_rejects_positional_and_query_lxm() -> None:
    assert RpcPermission.from_string('rpc:com.example.method1?aud=did:web:example.com&lxm=com.example.method2') is None


def test_rpc_permission_rejects_wildcard_aud_and_lxm() -> None:
    assert RpcPermission.from_string('rpc?aud=*&lxm=*') is None
    assert RpcPermission.from_string('rpc:*?aud=*') is None


@pytest.mark.parametrize(
    'invalid',
    [
        'rpc:*',
        'invalid',
        'rpc:invalid',
        'rpc:com.example.service',
        'rpc:invalid?aud=did:web:example.com',
        'rpc:com.example.service?aud=invalid',
        'rpc?lxm=invalid&aud=invalid',
    ],
)
def test_rpc_permission_rejects_invalid(invalid: str) -> None:
    assert RpcPermission.from_string(invalid) is None


def test_rpc_permission_matches_exact() -> None:
    scope = RpcPermission.from_string('rpc:com.example.service?aud=did:web:example.com%23service_id')
    assert scope is not None
    assert scope.matches(lxm='com.example.service', aud='did:web:example.com#service_id')


def test_rpc_permission_not_matches_different_lxm() -> None:
    scope = RpcPermission.from_string('rpc:com.example.service?aud=did:web:example.com%23service_id')
    assert scope is not None
    assert not scope.matches(lxm='com.example.OtherService', aud='did:web:example.com#service_id')


def test_rpc_permission_not_matches_different_aud() -> None:
    scope = RpcPermission.from_string('rpc:com.example.service?aud=did:web:example.com%23service_id')
    assert scope is not None
    assert not scope.matches(lxm='com.example.service', aud='did:example:456#service_id')


def test_rpc_permission_matches_wildcard_aud() -> None:
    scope = RpcPermission.from_string('rpc:com.example.method1?aud=*')
    assert scope is not None
    assert scope.matches(lxm='com.example.method1', aud='did:web:example.com#service_id')


def test_rpc_permission_matches_wildcard_lxm() -> None:
    scope = RpcPermission.from_string('rpc:*?aud=did:web:example.com%23service_id')
    assert scope is not None
    assert scope.matches(lxm='com.example.method1', aud='did:web:example.com#service_id')


def test_rpc_permission_scope_needed_for() -> None:
    scope = RpcPermission.scope_needed_for(lxm='com.example.service', aud='did:web:example.com#service_id')
    assert scope == 'rpc:com.example.service?aud=did:web:example.com%23service_id'


def test_rpc_permission_format_with_fragment() -> None:
    scope = RpcPermission(aud='did:web:example.com#service_id', lxm=('com.example.service',))
    assert str(scope) == 'rpc:com.example.service?aud=did:web:example.com%23service_id'


def test_rpc_permission_simplifies_wildcard_lxm() -> None:
    scope = RpcPermission(
        aud='did:web:example.com#service_id',
        lxm=('*', 'com.example.method1'),
    )
    assert str(scope) == 'rpc:*?aud=did:web:example.com%23service_id'


@pytest.mark.parametrize(
    ('input_scope', 'expected'),
    [
        (
            'rpc:com.example.service?aud=did:web:example.com%23service_id',
            'rpc:com.example.service?aud=did:web:example.com%23service_id',
        ),
        (
            'rpc:com.example.service?aud=did:web:example.com#service_id',
            'rpc:com.example.service?aud=did:web:example.com%23service_id',
        ),
        (
            'rpc?lxm=com.example.method1&lxm=com.example.method2&aud=*',
            'rpc?lxm=com.example.method1&lxm=com.example.method2&aud=*',
        ),
        (
            'rpc?lxm=com.example.method1&lxm=com.example.method2&lxm=*&aud=did:web:example.com%23service_id',
            'rpc:*?aud=did:web:example.com%23service_id',
        ),
        (
            'rpc?aud=did:web:example.com%23foo&lxm=com.example.service',
            'rpc:com.example.service?aud=did:web:example.com%23foo',
        ),
        (
            'rpc?lxm=com.example.method1&aud=did:web:example.com#foo',
            'rpc:com.example.method1?aud=did:web:example.com%23foo',
        ),
        (
            'rpc:com.example.method1?&aud=*',
            'rpc:com.example.method1?aud=*',
        ),
    ],
)
def test_rpc_permission_normalization_roundtrip(input_scope: str, expected: str) -> None:
    result = RpcPermission.from_string(input_scope)
    assert result is not None, f'Failed to parse {input_scope}'
    assert str(result) == expected


def test_account_permission_parse_email_default_action() -> None:
    scope = AccountPermission.from_string('account:email')
    assert scope is not None
    assert scope.attr == 'email'
    assert scope.action == ('read',)


def test_account_permission_parse_with_manage() -> None:
    scope = AccountPermission.from_string('account:repo?action=manage')
    assert scope is not None
    assert scope.attr == 'repo'
    assert scope.action == ('manage',)


def test_account_permission_manage_implies_read() -> None:
    scope = AccountPermission.from_string('account:repo?action=manage')
    assert scope is not None
    assert scope.matches(attr='repo', action='read')
    assert scope.matches(attr='repo', action='manage')


def test_account_permission_read_does_not_imply_manage() -> None:
    scope = AccountPermission.from_string('account:email')
    assert scope is not None
    assert scope.matches(attr='email', action='read')
    assert not scope.matches(attr='email', action='manage')


def test_account_permission_attr_must_match() -> None:
    scope = AccountPermission.from_string('account:email')
    assert scope is not None
    assert not scope.matches(attr='repo', action='read')


@pytest.mark.parametrize('attr', ['email', 'repo', 'status'])
def test_account_permission_all_attributes(attr: str) -> None:
    scope = AccountPermission.from_string(f'account:{attr}')
    assert scope is not None
    assert scope.attr == attr


def test_account_permission_rejects_invalid_attribute() -> None:
    assert AccountPermission.from_string('account:invalid') is None


def test_account_permission_scope_needed_for() -> None:
    assert AccountPermission.scope_needed_for(attr='email', action='read') == 'account:email'
    assert AccountPermission.scope_needed_for(attr='repo', action='manage') == 'account:repo?action=manage'


def test_identity_permission_parse_handle() -> None:
    scope = IdentityPermission.from_string('identity:handle')
    assert scope is not None
    assert scope.attr == 'handle'


def test_identity_permission_parse_wildcard() -> None:
    scope = IdentityPermission.from_string('identity:*')
    assert scope is not None
    assert scope.attr == '*'


def test_identity_permission_wildcard_matches_handle() -> None:
    scope = IdentityPermission.from_string('identity:*')
    assert scope is not None
    assert scope.matches('handle')


def test_identity_permission_handle_matches_handle() -> None:
    scope = IdentityPermission.from_string('identity:handle')
    assert scope is not None
    assert scope.matches('handle')


def test_identity_permission_handle_does_not_match_wildcard() -> None:
    scope = IdentityPermission.from_string('identity:handle')
    assert scope is not None
    assert not scope.matches('*')


def test_identity_permission_rejects_invalid() -> None:
    assert IdentityPermission.from_string('identity:invalid') is None
    assert IdentityPermission.from_string('invalid') is None


def test_include_scope_parse() -> None:
    scope = IncludeScope.from_string('include:com.example.appPermissions')
    assert scope is not None
    assert scope.nsid == 'com.example.appPermissions'
    assert scope.aud is None


def test_include_scope_parse_with_aud() -> None:
    scope = IncludeScope.from_string('include:com.example.appPermissions?aud=did:web:example.com%23service')
    assert scope is not None
    assert scope.nsid == 'com.example.appPermissions'
    assert scope.aud == 'did:web:example.com#service'


def test_include_scope_is_parent_authority_of_same_namespace() -> None:
    scope = IncludeScope(nsid='com.example.appPermissions')
    assert scope.is_parent_authority_of('com.example.record')
    assert scope.is_parent_authority_of('com.example.like')


def test_include_scope_is_parent_authority_of_different_namespace() -> None:
    scope = IncludeScope(nsid='com.example.appPermissions')
    assert not scope.is_parent_authority_of('com.other.thing')


def test_include_scope_is_parent_authority_of_wildcard() -> None:
    scope = IncludeScope(nsid='com.example.appPermissions')
    assert not scope.is_parent_authority_of('*')


def test_include_scope_rejects_invalid_nsid() -> None:
    assert IncludeScope.from_string('include:invalid') is None
    assert IncludeScope.from_string('include:a.b') is None


def test_include_scope_format_roundtrip() -> None:
    scope = IncludeScope(nsid='com.example.appPermissions')
    assert str(scope) == 'include:com.example.appPermissions'


def test_scopes_set_empty_set() -> None:
    ss = ScopesSet()
    assert ss.size == 0


def test_scopes_set_add_and_has() -> None:
    ss = ScopesSet()
    ss.add('repo:read')
    assert ss.size == 1
    assert ss.has('repo:read')
    assert not ss.has('repo:write')


def test_scopes_set_discard() -> None:
    ss = ScopesSet(['repo:read'])
    ss.discard('repo:read')
    assert ss.size == 0


def test_scopes_set_from_string() -> None:
    ss = ScopesSet.from_string('atproto repo:com.example.foo blob:*/*')
    assert ss.has('atproto')
    assert ss.has('repo:com.example.foo')
    assert ss.has('blob:*/*')


def test_scopes_set_matches_repo() -> None:
    ss = ScopesSet(['repo:com.example.foo'])
    assert ss.matches('repo', collection='com.example.foo', action='create')
    assert not ss.matches('repo', collection='com.example.bar', action='create')


def test_scopes_set_not_matches_action() -> None:
    ss = ScopesSet(['repo:com.example.foo?action=create'])
    assert not ss.matches('repo', collection='com.example.foo', action='delete')


def test_scopes_set_not_matches_invalid_scope() -> None:
    ss = ScopesSet(['repo:not-a-valid-nsid'])
    assert not ss.matches('repo', collection='not-a-valid-nsid', action='create')


def test_scopes_set_assert_matches_raises() -> None:
    ss = ScopesSet(['repo:com.example.foo'])
    with pytest.raises(ScopeMissingError) as exc_info:
        ss.assert_matches('repo', collection='com.example.bar', action='create')

    assert 'com.example.bar' in exc_info.value.scope


def test_scope_permissions_allows_repo() -> None:
    perms = ScopePermissions('repo:com.example.foo blob:*/*')
    assert perms.allows_repo('com.example.foo', 'create')
    assert not perms.allows_repo('com.example.bar', 'create')


def test_scope_permissions_allows_blob() -> None:
    perms = ScopePermissions('blob:*/*')
    assert perms.allows_blob('image/png')


def test_scope_permissions_allows_rpc() -> None:
    perms = ScopePermissions('rpc:com.example.foo?aud=*')
    assert perms.allows_rpc('com.example.foo', 'did:web:example.com')


def test_scope_permissions_allows_account() -> None:
    perms = ScopePermissions('account:email')
    assert perms.allows_account('email', 'read')
    assert not perms.allows_account('email', 'manage')


def test_scope_permissions_allows_identity() -> None:
    perms = ScopePermissions('identity:*')
    assert perms.allows_identity('handle')


def test_scope_permissions_assert_repo_raises() -> None:
    perms = ScopePermissions('repo:com.example.foo')
    with pytest.raises(ScopeMissingError):
        perms.assert_repo('com.example.bar', 'create')


def test_scope_permissions_transition_transition_email_allows_account_email_read() -> None:
    perms = ScopePermissionsTransition('transition:email account:repo')
    assert perms.allows_account('email', 'read')
    assert not perms.allows_account('email', 'manage')
    assert perms.allows_account('repo', 'read')
    assert not perms.allows_account('repo', 'manage')
    assert not perms.allows_account('status', 'read')


def test_scope_permissions_transition_transition_generic_allows_blob() -> None:
    perms = ScopePermissionsTransition('transition:generic')
    assert perms.allows_blob('foo/bar')


def test_scope_permissions_transition_transition_generic_allows_repo() -> None:
    perms = ScopePermissionsTransition('transition:generic')
    assert perms.allows_repo('app.bsky.feed.post', 'create')
    assert perms.allows_repo('app.bsky.feed.post', 'delete')
    assert perms.allows_repo('com.example.foo', 'create')


def test_scope_permissions_transition_transition_generic_allows_non_chat_rpc() -> None:
    perms = ScopePermissionsTransition('transition:generic')
    assert perms.allows_rpc('app.bsky.feed.post', 'did:web:example.com')
    assert perms.allows_rpc('com.example.foo', 'did:web:example.com')
    assert perms.allows_rpc('*', 'did:web:example.com')


def test_scope_permissions_transition_transition_generic_rejects_chat_rpc() -> None:
    perms = ScopePermissionsTransition('transition:generic')
    assert not perms.allows_rpc('chat.bsky.message.send', 'did:web:example.com')
    assert not perms.allows_rpc('chat.bsky.conversation.get', 'did:web:example.com')


def test_scope_permissions_transition_transition_chat_bsky_allows_chat_rpc() -> None:
    perms = ScopePermissionsTransition('transition:chat.bsky')
    assert perms.allows_rpc('chat.bsky.message.send', 'did:web:example.com')
    assert perms.allows_rpc('chat.bsky.conversation.get', 'did:web:example.com')


def test_scope_permissions_transition_transition_chat_bsky_rejects_non_chat_rpc() -> None:
    perms = ScopePermissionsTransition('transition:chat.bsky')
    assert not perms.allows_rpc('app.bsky.feed.post', 'did:web:example.com')
    assert not perms.allows_rpc('com.example.foo', 'did:web:example.com')
    assert not perms.allows_rpc('*', 'did:web:example.com')


def test_mime_is_mime_valid() -> None:
    assert is_mime('image/png')
    assert is_mime('application/json')


def test_mime_is_mime_rejects_wildcards() -> None:
    assert not is_mime('*/*')
    assert not is_mime('image/*')


def test_mime_is_mime_rejects_invalid() -> None:
    assert not is_mime('invalid')
    assert not is_mime('a/b/c')
    assert not is_mime('/png')
    assert not is_mime('image/')


def test_mime_is_accept_valid() -> None:
    assert is_accept('*/*')
    assert is_accept('image/*')
    assert is_accept('image/png')


def test_mime_is_accept_rejects_invalid() -> None:
    assert not is_accept('invalid')
    assert not is_accept('*/png')
    assert not is_accept('*/**')


def test_mime_matches_accept_wildcard() -> None:
    assert matches_accept('*/*', 'image/png')


def test_mime_matches_accept_subtype_wildcard() -> None:
    assert matches_accept('image/*', 'image/png')
    assert not matches_accept('image/*', 'application/json')


def test_mime_matches_accept_exact() -> None:
    assert matches_accept('image/png', 'image/png')
    assert not matches_accept('image/png', 'image/jpeg')


def test_mime_matches_any_accept() -> None:
    patterns = ['image/png', 'image/jpeg']
    assert matches_any_accept(patterns, 'image/png')
    assert matches_any_accept(patterns, 'image/jpeg')
    assert not matches_any_accept(patterns, 'image/gif')


@pytest.mark.parametrize(
    ('scope', 'canonical'),
    [
        ('blob?accept=application/ld%2Bjson', 'blob?accept=application/ld+json'),
        ('repo?collection=%41.b.c', 'repo?collection=A.b.c'),
        ('repo:a.b.c?action=a!b', 'repo:a.b.c?action=a%21b'),
        ('repo:a.b.c?action=a%7Eb', 'repo:a.b.c?action=a%7Eb'),
        ("repo:a.b.c?action=a'(b)*", 'repo:a.b.c?action=a%27%28b%29*'),
        ("repo:a!b~c'(d)*", "repo:a!b~c'(d)*"),
        ('rpc:a.b.c?aud=did:web:x.test%23svc', 'rpc:a.b.c?aud=did:web:x.test%23svc'),
        ('repo:caf%C3%A9.b.c', 'repo:caf%C3%A9.b.c'),
        ('repo?collection=caf%C3%A9', 'repo?collection=caf%C3%A9'),
        ('repo?collection=a%2Fb%3Ac%2Cd%40e', 'repo?collection=a/b:c,d@e'),
        ('repo?collection=a&b=c%26d%3De', 'repo?collection=a&b=c%26d%3De'),
        ('repo?collection=a b', 'repo?collection=a+b'),
    ],
)
def test_scope_string_syntax_canonical_form(scope: str, canonical: str) -> None:
    assert str(ScopeStringSyntax.from_string(scope)) == canonical


_PERMISSIONS = {
    'repo': RepoPermission,
    'blob': BlobPermission,
    'rpc': RpcPermission,
    'account': AccountPermission,
    'identity': IdentityPermission,
    'include': IncludeScope,
}


@pytest.mark.parametrize(
    ('scope', 'canonical'),
    [
        ('repo:*', 'repo:*'),
        ('repo:*?action=create', 'repo:*?action=create'),
        ('repo:app.bsky.feed.post?action=create&action=delete', 'repo:app.bsky.feed.post?action=create&action=delete'),
        ('repo?collection=a.b.c&collection=d.e.f', 'repo?collection=a.b.c&collection=d.e.f'),
        ('repo:a.b.c?action=create&action=create', 'repo:a.b.c?action=create'),
        ('repo:a.b.c?action=delete&action=update&action=create', 'repo:a.b.c'),
        ('blob:*/*', 'blob:*/*'),
        ('blob?accept=image/*&accept=video/*', 'blob?accept=image/*&accept=video/*'),
        ('blob?accept=image/png&accept=image/*', 'blob:image/*'),
        ('blob?accept=image/png&accept=image/png', 'blob?accept=image/png'),
        ('rpc:*?aud=did:web:api.bsky.app%23bsky_appview', 'rpc:*?aud=did:web:api.bsky.app%23bsky_appview'),
        ('rpc:app.bsky.actor.getProfile?aud=*', 'rpc:app.bsky.actor.getProfile?aud=*'),
        ('rpc?lxm=a.b.c&lxm=*&aud=did:web:x.test%23svc', 'rpc:*?aud=did:web:x.test%23svc'),
        ('account:email', 'account:email'),
        ('account:email?action=manage', 'account:email?action=manage'),
        ('account:email?action=read&action=manage', 'account:email?action=read&action=manage'),
        ('rpc:a.b.c?aud=did:web:localhost%253A2583%23svc', 'rpc:a.b.c?aud=did:web:localhost%3A2583%23svc'),
        ('account:repo?action=read', 'account:repo'),
        ('identity:handle', 'identity:handle'),
        ('identity:*', 'identity:*'),
        ('include:com.example.calendar.basePermissions', 'include:com.example.calendar.basePermissions'),
        ('include:com.example.set?aud=did:web:x.test%23svc', 'include:com.example.set?aud=did:web:x.test%23svc'),
    ],
)
def test_permission_canonical_form(scope: str, canonical: str) -> None:
    permission = _PERMISSIONS[scope.replace('?', ':').split(':')[0]].from_string(scope)

    assert permission is not None
    assert str(permission) == canonical


@pytest.mark.parametrize(
    'scope',
    [
        # the same parameter as a positional value and by name
        'repo:a.b.c?collection=d.e.f',
        'blob:image/png?accept=image/jpeg',
        'identity:%2A?attr=EMAIL&attr=email',
        # an empty value
        'repo:a.b.c?collection=',
        'repo:app.bsky.feed.like?action=&action=update',
        # several values for a parameter that takes one
        'rpc:a.b.c?aud=did:web:x.test%23svc&aud=did:web:y.test%23svc',
        'include:com.example.set?aud=did:web:x.test%23svc&aud=did:web:y.test%23svc',
        # an audience has to name a service, and only an RPC may use the wildcard
        'rpc:a.b.c',
        'rpc:*?aud=*',
        'rpc:app.bsky.feed.post?aud=did:web:api.bsky.app',
        'rpc:app.bsky.feed.post?aud=did:example:123%23svc',
        'rpc:app.bsky.feed.post?aud=did:web:example.com:path%23svc',
        'rpc:app.bsky.feed.post?aud=did:web:example.com%253A8443%23svc',
        'include:com.example.set?aud=*',
        'include:com.example.set?aud=did:web:x.test',
    ],
)
def test_invalid_permission_is_rejected(scope: str) -> None:
    assert _PERMISSIONS[scope.replace('?', ':').split(':')[0]].from_string(scope) is None
