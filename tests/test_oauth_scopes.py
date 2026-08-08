"""Tests for ATProto OAuth scope parsing library.

Ported from the TypeScript reference implementation test suite.
"""

from __future__ import annotations

import pytest
from atproto_oauth.client import _scopes_are_equivalent
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

# ---------------------------------------------------------------------------
# ScopeStringSyntax
# ---------------------------------------------------------------------------


class TestScopeStringSyntax:
    """Tests for scope string tokenizer."""

    @pytest.mark.parametrize(
        'scope,prefix,positional,params',
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
    def test_parse_scope(
        self,
        scope: str,
        prefix: str,
        positional: str | None,
        params: dict[str, list[str]],
    ) -> None:
        syntax = ScopeStringSyntax.from_string(scope)
        assert syntax.prefix == prefix
        assert syntax.positional == positional
        assert syntax.params == params

    def test_get_single_returns_none_for_absent(self) -> None:
        syntax = ScopeStringSyntax.from_string('my-res')
        assert syntax.get_single('nonexistent') is None

    def test_get_multi_returns_none_for_absent(self) -> None:
        syntax = ScopeStringSyntax.from_string('my-res')
        assert syntax.get_multi('nonexistent') is None

    def test_get_single_returns_none_for_multi_value(self) -> None:
        syntax = ScopeStringSyntax.from_string('my-res?x=foo&x=bar')
        assert syntax.get_single('x') is None

    def test_get_multi_returns_values(self) -> None:
        syntax = ScopeStringSyntax.from_string('my-res?x=foo&x=bar')
        assert syntax.get_multi('x') == ['foo', 'bar']

    def test_url_encoding_in_positional(self) -> None:
        syntax = ScopeStringSyntax.from_string('my-res:my%20pos')
        assert syntax.positional == 'my pos'

    def test_url_encoding_in_params(self) -> None:
        syntax = ScopeStringSyntax.from_string('my-res?x=my%20value')
        assert syntax.get_single('x') == 'my value'

    def test_colon_in_positional(self) -> None:
        syntax = ScopeStringSyntax.from_string('my-res:my:pos')
        assert syntax.positional == 'my:pos'

    def test_rpc_scope_with_did_in_params(self) -> None:
        """DID values in params contain colons which should not be treated as positional."""
        syntax = ScopeStringSyntax.from_string('rpc:foo.bar?aud=did:foo:bar?lxm=bar.baz')
        assert syntax.prefix == 'rpc'
        assert syntax.positional == 'foo.bar'
        # parse_qs splits on & only; the inner ? is part of the value
        aud_values = syntax.get_multi('aud')
        assert aud_values == ['did:foo:bar?lxm=bar.baz']


# ---------------------------------------------------------------------------
# RepoPermission
# ---------------------------------------------------------------------------


class TestRepoPermission:
    """Tests for repo permission parsing and matching."""

    def test_parse_positional(self) -> None:
        scope = RepoPermission.from_string('repo:com.example.foo')
        assert scope is not None
        assert scope.collection == ('com.example.foo',)
        assert scope.action == ('create', 'update', 'delete')

    def test_parse_with_actions(self) -> None:
        scope = RepoPermission.from_string('repo:com.example.foo?action=create&action=update')
        assert scope is not None
        assert scope.collection == ('com.example.foo',)
        assert scope.action == ('create', 'update')

    def test_parse_without_actions_defaults_to_all(self) -> None:
        scope = RepoPermission.from_string('repo:com.example.foo')
        assert scope is not None
        assert scope.action == ('create', 'update', 'delete')

    def test_wildcard_collection_with_action(self) -> None:
        scope = RepoPermission.from_string('repo:*?action=create')
        assert scope is not None
        assert scope.collection == ('*',)
        assert scope.action == ('create',)
        assert scope.matches(collection='any.collection.name', action='create')
        assert not scope.matches(collection='any.collection.name', action='update')

    def test_wildcard_collection_without_actions(self) -> None:
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
    def test_rejects_invalid(self, invalid: str) -> None:
        assert RepoPermission.from_string(invalid) is None

    def test_matches_create_action(self) -> None:
        scope = RepoPermission.from_string('repo:com.example.foo?action=create')
        assert scope is not None
        assert scope.matches(action='create', collection='com.example.foo')

    def test_not_matches_unspecified_action(self) -> None:
        scope = RepoPermission.from_string('repo:com.example.foo?action=create')
        assert scope is not None
        assert not scope.matches(action='update', collection='com.example.foo')

    def test_matches_wildcard_collection(self) -> None:
        scope = RepoPermission.from_string('repo:*?action=create')
        assert scope is not None
        assert scope.matches(action='create', collection='com.example.bar')

    def test_matches_multiple_actions(self) -> None:
        scope = RepoPermission.from_string('repo:com.example.foo?action=create&action=update')
        assert scope is not None
        assert scope.matches(action='create', collection='com.example.foo')
        assert scope.matches(action='update', collection='com.example.foo')
        assert not scope.matches(action='delete', collection='com.example.foo')

    def test_scope_needed_for(self) -> None:
        scope = RepoPermission.scope_needed_for(collection='com.example.foo', action='create')
        assert scope == 'repo:com.example.foo?action=create'

    def test_format(self) -> None:
        scope = RepoPermission(collection=('com.example.foo',), action=('create', 'update'))
        assert str(scope) == 'repo:com.example.foo?action=create&action=update'

    @pytest.mark.parametrize(
        'input_scope,expected',
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
    def test_normalization_roundtrip(self, input_scope: str, expected: str) -> None:
        result = RepoPermission.from_string(input_scope)
        assert result is not None
        assert str(result) == expected


# ---------------------------------------------------------------------------
# BlobPermission
# ---------------------------------------------------------------------------


class TestBlobPermission:
    """Tests for blob permission parsing and matching."""

    def test_parse_positional(self) -> None:
        scope = BlobPermission.from_string('blob:image/png')
        assert scope is not None
        assert scope.accept == ('image/png',)

    def test_parse_multiple_accept(self) -> None:
        scope = BlobPermission.from_string('blob?accept=image/png&accept=image/jpeg')
        assert scope is not None
        assert set(scope.accept) == {'image/png', 'image/jpeg'}

    def test_reject_without_accept(self) -> None:
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
    def test_rejects_invalid(self, invalid: str) -> None:
        assert BlobPermission.from_string(invalid) is None

    def test_matches_exact_mime(self) -> None:
        scope = BlobPermission.from_string('blob:image/png')
        assert scope is not None
        assert scope.matches('image/png')

    def test_matches_wildcard_all(self) -> None:
        scope = BlobPermission.from_string('blob:*/*')
        assert scope is not None
        assert scope.matches('image/jpeg')
        assert scope.matches('application/json')

    def test_matches_subtype_wildcard(self) -> None:
        scope = BlobPermission.from_string('blob:image/*')
        assert scope is not None
        assert scope.matches('image/gif')
        assert not scope.matches('application/json')

    def test_not_matches_different_mime(self) -> None:
        scope = BlobPermission.from_string('blob:image/png')
        assert scope is not None
        assert not scope.matches('image/jpeg')

    def test_matches_multiple_accept(self) -> None:
        scope = BlobPermission.from_string('blob?accept=image/png&accept=image/jpeg')
        assert scope is not None
        assert scope.matches('image/png')
        assert scope.matches('image/jpeg')
        assert not scope.matches('image/gif')

    def test_scope_needed_for(self) -> None:
        assert BlobPermission.scope_needed_for('image/png') == 'blob:image/png'

    def test_strips_redundant_accept(self) -> None:
        assert str(BlobPermission(accept=('*/*', 'image/*'))) == 'blob:*/*'
        assert str(BlobPermission(accept=('*/*', 'image/png'))) == 'blob:*/*'
        assert str(BlobPermission(accept=('image/*', 'image/png'))) == 'blob:image/*'

    def test_positional_format_for_single(self) -> None:
        assert str(BlobPermission(accept=('image/png',))) == 'blob:image/png'
        assert str(BlobPermission(accept=('image/*',))) == 'blob:image/*'
        assert str(BlobPermission(accept=('*/*',))) == 'blob:*/*'

    def test_query_format_for_multiple(self) -> None:
        result = str(BlobPermission(accept=('image/png', 'image/jpeg')))
        assert result == 'blob?accept=image/jpeg&accept=image/png'


# ---------------------------------------------------------------------------
# RpcPermission
# ---------------------------------------------------------------------------


class TestRpcPermission:
    """Tests for RPC permission parsing and matching."""

    def test_parse_positional_with_aud(self) -> None:
        scope = RpcPermission.from_string('rpc:com.example.service?aud=did:web:example.com%23service_id')
        assert scope is not None
        assert scope.aud == 'did:web:example.com#service_id'
        assert scope.lxm == ('com.example.service',)

    def test_parse_query_format(self) -> None:
        scope = RpcPermission.from_string('rpc?lxm=com.example.method1&aud=*')
        assert scope is not None
        assert scope.aud == '*'
        assert scope.lxm == ('com.example.method1',)

    def test_parse_positional_equivalent(self) -> None:
        scope = RpcPermission.from_string('rpc:com.example.method1?aud=*')
        assert scope is not None
        assert scope.aud == '*'
        assert scope.lxm == ('com.example.method1',)

    def test_parse_multiple_lxm(self) -> None:
        scope = RpcPermission.from_string('rpc?aud=*&lxm=com.example.method1&lxm=com.example.method2')
        assert scope is not None
        assert scope.aud == '*'
        assert scope.lxm == ('com.example.method1', 'com.example.method2')

    def test_rejects_without_lxm(self) -> None:
        assert RpcPermission.from_string('rpc?aud=did:web:example.com%23service_id') is None
        assert RpcPermission.from_string('rpc:?aud=did:web:example.com%23service_id') is None

    def test_rejects_without_aud(self) -> None:
        assert RpcPermission.from_string('rpc?lxm=com.example.method1') is None
        assert RpcPermission.from_string('rpc:com.example.method1') is None

    def test_rejects_positional_and_query_lxm(self) -> None:
        assert (
            RpcPermission.from_string('rpc:com.example.method1?aud=did:web:example.com&lxm=com.example.method2') is None
        )

    def test_rejects_wildcard_aud_and_lxm(self) -> None:
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
    def test_rejects_invalid(self, invalid: str) -> None:
        assert RpcPermission.from_string(invalid) is None

    def test_matches_exact(self) -> None:
        scope = RpcPermission.from_string('rpc:com.example.service?aud=did:web:example.com%23service_id')
        assert scope is not None
        assert scope.matches(lxm='com.example.service', aud='did:web:example.com#service_id')

    def test_not_matches_different_lxm(self) -> None:
        scope = RpcPermission.from_string('rpc:com.example.service?aud=did:web:example.com%23service_id')
        assert scope is not None
        assert not scope.matches(lxm='com.example.OtherService', aud='did:web:example.com#service_id')

    def test_not_matches_different_aud(self) -> None:
        scope = RpcPermission.from_string('rpc:com.example.service?aud=did:web:example.com%23service_id')
        assert scope is not None
        assert not scope.matches(lxm='com.example.service', aud='did:example:456#service_id')

    def test_matches_wildcard_aud(self) -> None:
        scope = RpcPermission.from_string('rpc:com.example.method1?aud=*')
        assert scope is not None
        assert scope.matches(lxm='com.example.method1', aud='did:web:example.com#service_id')

    def test_matches_wildcard_lxm(self) -> None:
        scope = RpcPermission.from_string('rpc:*?aud=did:web:example.com%23service_id')
        assert scope is not None
        assert scope.matches(lxm='com.example.method1', aud='did:web:example.com#service_id')

    def test_scope_needed_for(self) -> None:
        scope = RpcPermission.scope_needed_for(lxm='com.example.service', aud='did:web:example.com#service_id')
        assert scope == 'rpc:com.example.service?aud=did:web:example.com%23service_id'

    def test_format_with_fragment(self) -> None:
        scope = RpcPermission(aud='did:web:example.com#service_id', lxm=('com.example.service',))
        assert str(scope) == 'rpc:com.example.service?aud=did:web:example.com%23service_id'

    def test_simplifies_wildcard_lxm(self) -> None:
        scope = RpcPermission(
            aud='did:web:example.com#service_id',
            lxm=('*', 'com.example.method1'),
        )
        assert str(scope) == 'rpc:*?aud=did:web:example.com%23service_id'

    @pytest.mark.parametrize(
        'input_scope,expected',
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
    def test_normalization_roundtrip(self, input_scope: str, expected: str) -> None:
        result = RpcPermission.from_string(input_scope)
        assert result is not None, f'Failed to parse {input_scope}'
        assert str(result) == expected


# ---------------------------------------------------------------------------
# AccountPermission
# ---------------------------------------------------------------------------


class TestAccountPermission:
    """Tests for account permission parsing and matching."""

    def test_parse_email_default_action(self) -> None:
        scope = AccountPermission.from_string('account:email')
        assert scope is not None
        assert scope.attr == 'email'
        assert scope.action == ('read',)

    def test_parse_with_manage(self) -> None:
        scope = AccountPermission.from_string('account:repo?action=manage')
        assert scope is not None
        assert scope.attr == 'repo'
        assert scope.action == ('manage',)

    def test_manage_implies_read(self) -> None:
        scope = AccountPermission.from_string('account:repo?action=manage')
        assert scope is not None
        assert scope.matches(attr='repo', action='read')
        assert scope.matches(attr='repo', action='manage')

    def test_read_does_not_imply_manage(self) -> None:
        scope = AccountPermission.from_string('account:email')
        assert scope is not None
        assert scope.matches(attr='email', action='read')
        assert not scope.matches(attr='email', action='manage')

    def test_attr_must_match(self) -> None:
        scope = AccountPermission.from_string('account:email')
        assert scope is not None
        assert not scope.matches(attr='repo', action='read')

    @pytest.mark.parametrize('attr', ['email', 'repo', 'status'])
    def test_all_attributes(self, attr: str) -> None:
        scope = AccountPermission.from_string(f'account:{attr}')
        assert scope is not None
        assert scope.attr == attr

    def test_rejects_invalid_attribute(self) -> None:
        assert AccountPermission.from_string('account:invalid') is None

    def test_scope_needed_for(self) -> None:
        assert AccountPermission.scope_needed_for(attr='email', action='read') == 'account:email'
        assert AccountPermission.scope_needed_for(attr='repo', action='manage') == 'account:repo?action=manage'


# ---------------------------------------------------------------------------
# IdentityPermission
# ---------------------------------------------------------------------------


class TestIdentityPermission:
    """Tests for identity permission parsing and matching."""

    def test_parse_handle(self) -> None:
        scope = IdentityPermission.from_string('identity:handle')
        assert scope is not None
        assert scope.attr == 'handle'

    def test_parse_wildcard(self) -> None:
        scope = IdentityPermission.from_string('identity:*')
        assert scope is not None
        assert scope.attr == '*'

    def test_wildcard_matches_handle(self) -> None:
        scope = IdentityPermission.from_string('identity:*')
        assert scope is not None
        assert scope.matches('handle')

    def test_handle_matches_handle(self) -> None:
        scope = IdentityPermission.from_string('identity:handle')
        assert scope is not None
        assert scope.matches('handle')

    def test_handle_does_not_match_wildcard(self) -> None:
        scope = IdentityPermission.from_string('identity:handle')
        assert scope is not None
        assert not scope.matches('*')

    def test_rejects_invalid(self) -> None:
        assert IdentityPermission.from_string('identity:invalid') is None
        assert IdentityPermission.from_string('invalid') is None


# ---------------------------------------------------------------------------
# IncludeScope
# ---------------------------------------------------------------------------


class TestIncludeScope:
    """Tests for include scope parsing."""

    def test_parse(self) -> None:
        scope = IncludeScope.from_string('include:fm.plyr.authFullApp')
        assert scope is not None
        assert scope.nsid == 'fm.plyr.authFullApp'
        assert scope.aud is None

    def test_parse_with_aud(self) -> None:
        scope = IncludeScope.from_string('include:fm.plyr.authFullApp?aud=did:web:example.com')
        assert scope is not None
        assert scope.nsid == 'fm.plyr.authFullApp'
        assert scope.aud == 'did:web:example.com'

    def test_is_parent_authority_of_same_namespace(self) -> None:
        scope = IncludeScope(nsid='fm.plyr.authFullApp')
        assert scope.is_parent_authority_of('fm.plyr.track')
        assert scope.is_parent_authority_of('fm.plyr.like')

    def test_is_parent_authority_of_different_namespace(self) -> None:
        scope = IncludeScope(nsid='fm.plyr.authFullApp')
        assert not scope.is_parent_authority_of('com.other.thing')

    def test_is_parent_authority_of_wildcard(self) -> None:
        scope = IncludeScope(nsid='fm.plyr.authFullApp')
        assert not scope.is_parent_authority_of('*')

    def test_rejects_invalid_nsid(self) -> None:
        assert IncludeScope.from_string('include:invalid') is None
        assert IncludeScope.from_string('include:a.b') is None

    def test_format_roundtrip(self) -> None:
        scope = IncludeScope(nsid='fm.plyr.authFullApp')
        assert str(scope) == 'include:fm.plyr.authFullApp'


# ---------------------------------------------------------------------------
# ScopesSet
# ---------------------------------------------------------------------------


class TestScopesSet:
    """Tests for the ScopesSet container."""

    def test_empty_set(self) -> None:
        ss = ScopesSet()
        assert ss.size == 0

    def test_add_and_has(self) -> None:
        ss = ScopesSet()
        ss.add('repo:read')
        assert ss.size == 1
        assert ss.has('repo:read')
        assert not ss.has('repo:write')

    def test_discard(self) -> None:
        ss = ScopesSet(['repo:read'])
        ss.discard('repo:read')
        assert ss.size == 0

    def test_from_string(self) -> None:
        ss = ScopesSet.from_string('atproto repo:com.example.foo blob:*/*')
        assert ss.has('atproto')
        assert ss.has('repo:com.example.foo')
        assert ss.has('blob:*/*')

    def test_matches_repo(self) -> None:
        ss = ScopesSet(['repo:com.example.foo'])
        assert ss.matches('repo', collection='com.example.foo', action='create')
        assert not ss.matches('repo', collection='com.example.bar', action='create')

    def test_not_matches_action(self) -> None:
        ss = ScopesSet(['repo:com.example.foo?action=create'])
        assert not ss.matches('repo', collection='com.example.foo', action='delete')

    def test_not_matches_invalid_scope(self) -> None:
        ss = ScopesSet(['repo:not-a-valid-nsid'])
        assert not ss.matches('repo', collection='not-a-valid-nsid', action='create')

    def test_assert_matches_raises(self) -> None:
        ss = ScopesSet(['repo:com.example.foo'])
        with pytest.raises(ScopeMissingError) as exc_info:
            ss.assert_matches('repo', collection='com.example.bar', action='create')
        assert 'com.example.bar' in exc_info.value.scope


# ---------------------------------------------------------------------------
# ScopePermissions
# ---------------------------------------------------------------------------


class TestScopePermissions:
    """Tests for the typed ScopePermissions facade."""

    def test_allows_repo(self) -> None:
        perms = ScopePermissions('repo:com.example.foo blob:*/*')
        assert perms.allows_repo('com.example.foo', 'create')
        assert not perms.allows_repo('com.example.bar', 'create')

    def test_allows_blob(self) -> None:
        perms = ScopePermissions('blob:*/*')
        assert perms.allows_blob('image/png')

    def test_allows_rpc(self) -> None:
        perms = ScopePermissions('rpc:com.example.foo?aud=*')
        assert perms.allows_rpc('com.example.foo', 'did:web:example.com')

    def test_allows_account(self) -> None:
        perms = ScopePermissions('account:email')
        assert perms.allows_account('email', 'read')
        assert not perms.allows_account('email', 'manage')

    def test_allows_identity(self) -> None:
        perms = ScopePermissions('identity:*')
        assert perms.allows_identity('handle')

    def test_assert_repo_raises(self) -> None:
        perms = ScopePermissions('repo:com.example.foo')
        with pytest.raises(ScopeMissingError):
            perms.assert_repo('com.example.bar', 'create')


# ---------------------------------------------------------------------------
# ScopePermissionsTransition
# ---------------------------------------------------------------------------


class TestScopePermissionsTransition:
    """Tests for transition scope handling."""

    def test_transition_email_allows_account_email_read(self) -> None:
        perms = ScopePermissionsTransition('transition:email account:repo')
        assert perms.allows_account('email', 'read')
        assert not perms.allows_account('email', 'manage')
        assert perms.allows_account('repo', 'read')
        assert not perms.allows_account('repo', 'manage')
        assert not perms.allows_account('status', 'read')

    def test_transition_generic_allows_blob(self) -> None:
        perms = ScopePermissionsTransition('transition:generic')
        assert perms.allows_blob('foo/bar')

    def test_transition_generic_allows_repo(self) -> None:
        perms = ScopePermissionsTransition('transition:generic')
        assert perms.allows_repo('app.bsky.feed.post', 'create')
        assert perms.allows_repo('app.bsky.feed.post', 'delete')
        assert perms.allows_repo('com.example.foo', 'create')

    def test_transition_generic_allows_non_chat_rpc(self) -> None:
        perms = ScopePermissionsTransition('transition:generic')
        assert perms.allows_rpc('app.bsky.feed.post', 'did:web:example.com')
        assert perms.allows_rpc('com.example.foo', 'did:web:example.com')
        assert perms.allows_rpc('*', 'did:web:example.com')

    def test_transition_generic_rejects_chat_rpc(self) -> None:
        perms = ScopePermissionsTransition('transition:generic')
        assert not perms.allows_rpc('chat.bsky.message.send', 'did:web:example.com')
        assert not perms.allows_rpc('chat.bsky.conversation.get', 'did:web:example.com')

    def test_transition_chat_bsky_allows_chat_rpc(self) -> None:
        perms = ScopePermissionsTransition('transition:chat.bsky')
        assert perms.allows_rpc('chat.bsky.message.send', 'did:web:example.com')
        assert perms.allows_rpc('chat.bsky.conversation.get', 'did:web:example.com')

    def test_transition_chat_bsky_rejects_non_chat_rpc(self) -> None:
        perms = ScopePermissionsTransition('transition:chat.bsky')
        assert not perms.allows_rpc('app.bsky.feed.post', 'did:web:example.com')
        assert not perms.allows_rpc('com.example.foo', 'did:web:example.com')
        assert not perms.allows_rpc('*', 'did:web:example.com')


# ---------------------------------------------------------------------------
# _scopes_are_equivalent
# ---------------------------------------------------------------------------


class TestScopesAreEquivalent:
    """Tests for the SDK-level scope equivalence check."""

    def test_exact_match(self) -> None:
        assert _scopes_are_equivalent(
            'atproto repo:fm.plyr.track',
            'atproto repo:fm.plyr.track',
        )

    def test_format_equivalence(self) -> None:
        """repo:nsid == repo?collection=nsid."""
        assert _scopes_are_equivalent(
            'atproto repo:fm.plyr.track',
            'atproto repo?collection=fm.plyr.track',
        )

    def test_include_expansion(self) -> None:
        """include:namespace.permSet is satisfied by repo?collection= in that namespace."""
        assert _scopes_are_equivalent(
            'atproto include:fm.plyr.authFullApp',
            'atproto repo?collection=fm.plyr.track&collection=fm.plyr.like',
        )

    def test_include_expansion_with_positional(self) -> None:
        """include:namespace.permSet is satisfied by repo:ns.collection."""
        assert _scopes_are_equivalent(
            'atproto include:fm.plyr.authFullApp',
            'atproto repo:fm.plyr.track repo:fm.plyr.like',
        )

    def test_missing_scope(self) -> None:
        assert not _scopes_are_equivalent(
            'atproto repo:fm.plyr.track repo:fm.plyr.like',
            'atproto repo:fm.plyr.track',
        )

    def test_extra_granted_ok(self) -> None:
        assert _scopes_are_equivalent(
            'atproto repo:fm.plyr.track',
            'atproto repo:fm.plyr.track repo:fm.plyr.like blob:*/*',
        )

    def test_include_wrong_namespace(self) -> None:
        assert not _scopes_are_equivalent(
            'atproto include:fm.plyr.authFullApp',
            'atproto repo?collection=com.other.thing',
        )

    def test_transition_scopes_exact_match(self) -> None:
        assert _scopes_are_equivalent(
            'atproto transition:generic',
            'atproto transition:generic',
        )

    def test_transition_scopes_missing(self) -> None:
        assert not _scopes_are_equivalent(
            'atproto transition:generic',
            'atproto repo:com.example.foo',
        )

    def test_blob_equivalence(self) -> None:
        assert _scopes_are_equivalent(
            'atproto blob:*/*',
            'atproto blob:*/*',
        )

    def test_empty_scopes(self) -> None:
        assert _scopes_are_equivalent('', '')

    def test_repo_wildcard_covers_specific(self) -> None:
        """repo:* should cover any specific collection."""
        assert _scopes_are_equivalent(
            'atproto repo:fm.plyr.track',
            'atproto repo:*',
        )

    def test_action_mismatch(self) -> None:
        """repo with limited actions should not cover all-action request."""
        assert not _scopes_are_equivalent(
            'atproto repo:fm.plyr.track',
            'atproto repo:fm.plyr.track?action=create',
        )

    def test_blob_wildcard_covers_specific(self) -> None:
        """granted blob:*/* should cover requested blob:image/png."""
        assert _scopes_are_equivalent(
            'atproto blob:image/png',
            'atproto blob:*/*',
        )

    def test_granted_superset_actions(self) -> None:
        """granted all-actions should cover limited-action request."""
        assert _scopes_are_equivalent(
            'atproto repo:fm.plyr.track?action=create',
            'atproto repo:fm.plyr.track',
        )


# ---------------------------------------------------------------------------
# MIME helpers
# ---------------------------------------------------------------------------


class TestMime:
    """Tests for MIME matching utilities."""

    def test_is_mime_valid(self) -> None:
        assert is_mime('image/png')
        assert is_mime('application/json')

    def test_is_mime_rejects_wildcards(self) -> None:
        assert not is_mime('*/*')
        assert not is_mime('image/*')

    def test_is_mime_rejects_invalid(self) -> None:
        assert not is_mime('invalid')
        assert not is_mime('a/b/c')
        assert not is_mime('/png')
        assert not is_mime('image/')

    def test_is_accept_valid(self) -> None:
        assert is_accept('*/*')
        assert is_accept('image/*')
        assert is_accept('image/png')

    def test_is_accept_rejects_invalid(self) -> None:
        assert not is_accept('invalid')
        assert not is_accept('*/png')
        assert not is_accept('*/**')

    def test_matches_accept_wildcard(self) -> None:
        assert matches_accept('*/*', 'image/png')

    def test_matches_accept_subtype_wildcard(self) -> None:
        assert matches_accept('image/*', 'image/png')
        assert not matches_accept('image/*', 'application/json')

    def test_matches_accept_exact(self) -> None:
        assert matches_accept('image/png', 'image/png')
        assert not matches_accept('image/png', 'image/jpeg')

    def test_matches_any_accept(self) -> None:
        patterns = ['image/png', 'image/jpeg']
        assert matches_any_accept(patterns, 'image/png')
        assert matches_any_accept(patterns, 'image/jpeg')
        assert not matches_any_accept(patterns, 'image/gif')
