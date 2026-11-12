import dataclasses
import json
import stat
import time
import typing as t
from pathlib import Path

import pytest
from atproto_crypto.jwk import generate_p256_jwk
from atproto_oauth._effects import call
from atproto_oauth.exceptions import UnsupportedAuthServerError
from atproto_oauth.keys import Keyset
from atproto_oauth.metadata import (
    AuthServerMetadata,
    _is_origin,
    build_client_metadata,
    build_loopback_client_id,
    validate_client_metadata,
)
from atproto_oauth.models import AuthMethod, OAuthSessionData, OAuthStateData, TokenInfo, TokenResponse, TokenSet
from atproto_oauth.stores import JsonFileStore, MemoryStore

CLIENT_ID = 'https://app.example.com/client-metadata.json'
REDIRECT_URI = 'https://app.example.com/callback'


def test_loopback_client_id() -> None:
    assert build_loopback_client_id() == 'http://localhost'
    assert build_loopback_client_id(['http://127.0.0.1/', 'http://[::1]/'], 'atproto') == 'http://localhost'
    assert build_loopback_client_id(scope='atproto transition:generic') == (
        'http://localhost?scope=atproto+transition%3Ageneric'
    )
    # the port is not part of the client ID, so it may be picked at run time
    assert build_loopback_client_id(['http://127.0.0.1:8765/callback', 'http://[::1]:9000/callback']) == (
        'http://localhost?redirect_uri=http%3A%2F%2F127.0.0.1%2Fcallback&redirect_uri=http%3A%2F%2F%5B%3A%3A1%5D%2Fcallback'
    )


@pytest.mark.parametrize(
    'redirect_uri',
    ['http://localhost/callback', 'https://127.0.0.1/callback', 'http://example.com/callback', 'http://10.0.0.1/'],
)
def test_loopback_redirect_uri_must_be_an_ip_literal(redirect_uri: str) -> None:
    with pytest.raises(ValueError, match='must be an http URL'):
        build_loopback_client_id([redirect_uri])


def test_loopback_scope_must_include_atproto() -> None:
    with pytest.raises(ValueError, match='atproto'):
        build_loopback_client_id(scope='transition:generic')


def test_public_client_metadata() -> None:
    metadata = build_client_metadata(CLIENT_ID, [REDIRECT_URI], 'atproto', client_name='Example')

    assert metadata == {
        'client_id': CLIENT_ID,
        'application_type': 'web',
        'grant_types': ['authorization_code', 'refresh_token'],
        'response_types': ['code'],
        'redirect_uris': [REDIRECT_URI],
        'scope': 'atproto',
        'dpop_bound_access_tokens': True,
        'token_endpoint_auth_method': 'none',
        'client_name': 'Example',
    }


def test_loopback_client_metadata() -> None:
    client_id = build_loopback_client_id(['http://127.0.0.1:8765/cb'])
    metadata = build_client_metadata(client_id, ['http://127.0.0.1:8765/cb'], 'atproto')

    assert metadata['application_type'] == 'native'
    assert metadata['token_endpoint_auth_method'] == 'none'


def test_confidential_client_metadata() -> None:
    keyset = Keyset([generate_p256_jwk(kid='key-1'), generate_p256_jwk(kid='key-2')])
    metadata = build_client_metadata(CLIENT_ID, [REDIRECT_URI], 'atproto', keyset)

    assert metadata['token_endpoint_auth_method'] == 'private_key_jwt'
    assert metadata['token_endpoint_auth_signing_alg'] == 'ES256'
    assert [key['kid'] for key in metadata['jwks']['keys']] == ['key-1', 'key-2']
    for key in metadata['jwks']['keys']:
        assert set(key) == {'kty', 'crv', 'x', 'y', 'kid', 'use', 'alg'}

    hosted = build_client_metadata(
        CLIENT_ID, [REDIRECT_URI], 'atproto', keyset, jwks_uri='https://app.example.com/jwks.json'
    )
    assert 'jwks' not in hosted


@pytest.mark.parametrize(
    ('client_id', 'message'),
    [
        ('http://app.example.com/client-metadata.json', 'https URL'),
        ('https://app.example.com', 'path'),
        ('https://app.example.com/', 'path'),
        ('https://app.example.com/dir/', 'path'),
        ('https://app.example.com:8443/client-metadata.json', 'port'),
        ('https://8.8.8.8/client-metadata.json', 'IP address'),
        ('https://app.example.com/client-metadata.json#frag', 'fragment'),
        ('http://localhost:8080', 'optional query'),
        ('http://localhost/path', 'optional query'),
        ('http://localhost?redirect_uri=http%3A%2F%2Fexample.com%2F', 'Invalid redirect URI'),
        ('http://localhost?foo=bar', 'Unexpected parameter'),
        ('http://localhost?scope=atproto&scope=atproto', 'scope twice'),
        ('http://localhost?scope=', 'single spaces'),
        ('http://localhost?scope=atproto++transition%3Ageneric', 'single spaces'),
        ('http://localhost?scope=transition%3Ageneric', 'must include'),
        ('http://localhost?redirect_uri=HTTP%3A%2F%2F127.0.0.1%2F', 'Invalid redirect URI'),
        ('http://localhost?redirect_uri=http%3A%2F%2Fuser%40127.0.0.1%2F', 'Invalid redirect URI'),
        ('HTTPS://app.example.com/client-metadata.json', 'https URL'),
        ('https://example/client-metadata.json', 'domain name'),
        ('https://app.example.local/client-metadata.json', 'domain name'),
        ('https://ex ample.com/client-metadata.json', 'domain name'),
        ('https://user@app.example.com/client-metadata.json', 'credentials'),
        ('https://app.example.com/a/../client-metadata.json', 'canonical form'),
        ('https://app.example.com/a/./client-metadata.json', 'canonical form'),
        ('https://app.example.com/%2e%2e/client-metadata.json', 'canonical form'),
        ('https://app.example.com/client metadata.json', 'canonical form'),
    ],
)
def test_client_id_rules(client_id: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        build_client_metadata(client_id, [REDIRECT_URI], 'atproto')


@pytest.mark.parametrize(
    ('change', 'message'),
    [
        ({'scope': 'transition:generic'}, 'atproto'),
        ({'redirect_uris': []}, 'redirect_uris'),
        ({'response_types': ['token']}, 'response_types'),
        ({'grant_types': ['refresh_token']}, 'grant_types'),
        ({'dpop_bound_access_tokens': False}, 'dpop_bound_access_tokens'),
        ({'token_endpoint_auth_method': 'client_secret_basic'}, 'token_endpoint_auth_method'),
        ({'token_endpoint_auth_signing_alg': 'ES256'}, 'must not be set'),
        ({'token_endpoint_auth_method': 'private_key_jwt'}, 'token_endpoint_auth_signing_alg'),
        (
            {'token_endpoint_auth_method': 'private_key_jwt', 'token_endpoint_auth_signing_alg': 'ES256'},
            'at least one client authentication key',
        ),
    ],
)
def test_client_metadata_rules(change: t.Dict[str, t.Any], message: str) -> None:
    metadata = {**build_client_metadata(CLIENT_ID, [REDIRECT_URI], 'atproto'), **change}

    with pytest.raises(ValueError, match=message):
        validate_client_metadata(metadata)


def test_published_jwks_must_contain_every_signing_key() -> None:
    keyset = Keyset([generate_p256_jwk(kid='key-1'), generate_p256_jwk(kid='key-2')])
    jwks = {'keys': keyset.public_jwks['keys'][:1]}

    with pytest.raises(ValueError, match='key-2'):
        build_client_metadata(CLIENT_ID, [REDIRECT_URI], 'atproto', keyset, jwks=jwks)

    with pytest.raises(ValueError, match='mutually exclusive'):
        build_client_metadata(
            CLIENT_ID, [REDIRECT_URI], 'atproto', keyset, jwks=keyset.public_jwks, jwks_uri='https://app.example.com/j'
        )


def test_keyset_rules() -> None:
    key = generate_p256_jwk(kid='key-1')

    with pytest.raises(ValueError, match='"kid"'):
        Keyset([generate_p256_jwk()])

    with pytest.raises(ValueError, match='Duplicate'):
        Keyset([key, key])

    with pytest.raises(ValueError, match='private P-256'):
        Keyset([{name: value for name, value in key.items() if name != 'd'}])

    keyset = Keyset([key, generate_p256_jwk(kid='key-2')])
    assert len(keyset) == 2
    default, second = keyset.default, keyset.get('key-2')
    assert default is not None
    assert second is not None
    assert (default.kid, second.kid) == ('key-1', 'key-2')
    assert keyset.get('missing') is None
    assert keyset.get(None) is None
    assert Keyset().default is None


def test_persisted_data_round_trips_through_json() -> None:
    token_set = TokenSet(
        iss='https://auth.test',
        sub='did:plc:alicealicealicealiceali2',
        aud='https://pds.test',
        scope='atproto',
        access_token='access',
        refresh_token='refresh',
        expires_at=1_800_000_000.5,
    )
    session = OAuthSessionData(generate_p256_jwk(), AuthMethod('private_key_jwt', 'key-1'), token_set)
    state = OAuthStateData(
        iss='https://auth.test',
        dpop_jwk=generate_p256_jwk(),
        auth_method=AuthMethod('none'),
        pkce_verifier='verifier',
        redirect_uri='http://127.0.0.1/',
        created_at=1_700_000_000.0,
        did='did:plc:alicealicealicealiceali2',
        app_state='app',
    )

    assert OAuthSessionData.from_dict(json.loads(json.dumps(session.to_dict()))) == session
    assert OAuthStateData.from_dict(json.loads(json.dumps(state.to_dict()))) == state
    # fields added by a later version are ignored
    assert OAuthSessionData.from_dict({**session.to_dict(), 'future': 1}) == session


@pytest.mark.parametrize(
    'change',
    [
        {'token_set': None},
        {'dpop_jwk': 'jwk'},
        {'auth_method': {'method': 'client_secret_basic'}},
        {'auth_method': {'method': 'private_key_jwt'}},
        {'auth_method': {'method': 'none', 'kid': 'key-1'}},
        {'token_set': {'iss': 'https://auth.test'}},
    ],
)
def test_invalid_persisted_data_is_rejected(change: t.Dict[str, t.Any]) -> None:
    token_set = TokenSet(
        'https://auth.test', 'did:plc:alicealicealicealiceali2', 'https://pds.test', 'atproto', 'access'
    )
    data = {**OAuthSessionData(generate_p256_jwk(), AuthMethod('none'), token_set).to_dict(), **change}

    with pytest.raises(ValueError, match=r'missing or invalid|is invalid'):
        OAuthSessionData.from_dict(data)


def test_token_info() -> None:
    token_set = TokenSet(
        'https://auth.test', 'did:plc:alicealicealicealiceali2', 'https://pds.test', 'atproto', 'access'
    )
    assert TokenInfo.from_token_set(token_set).expired is None

    expired = dataclasses.replace(token_set, expires_at=time.time() - 60)
    assert TokenInfo.from_token_set(expired).expired is True
    assert 'access' not in repr(TokenInfo.from_token_set(expired))


def test_memory_store() -> None:
    store: MemoryStore[str] = MemoryStore(ttl=0.05, max_size=2)
    store.set('a', '1')
    store.set('b', '2')
    store.set('c', '3')

    assert store.get('a') is None
    assert store.get('b') == '2'
    store.delete('b')
    store.delete('missing')
    assert store.get('b') is None

    time.sleep(0.1)
    assert store.get('c') is None


def test_json_file_store(tmp_path: Path) -> None:
    path = tmp_path / 'sessions.json'
    store = JsonFileStore(path)
    token_set = TokenSet(
        'https://auth.test', 'did:plc:alicealicealicealiceali2', 'https://pds.test', 'atproto', 'access'
    )
    session = OAuthSessionData(generate_p256_jwk(), AuthMethod('none'), token_set)

    assert store.get('did:plc:alicealicealicealiceali2') is None
    store.delete('did:plc:alicealicealicealiceali2')
    assert not path.exists()

    store.set('did:plc:alicealicealicealiceali2', session)
    store.set('did:plc:bobbobbobbobbobbobbobbob', {'other': 1})

    assert stat.S_IMODE(path.stat().st_mode) == 0o600
    assert list(tmp_path.iterdir()) == [path]

    reopened = JsonFileStore(str(path))
    stored = reopened.get('did:plc:alicealicealicealiceali2')
    assert stored is not None
    assert OAuthSessionData.from_dict(stored) == session

    reopened.delete('did:plc:alicealicealicealiceali2')
    assert store.get('did:plc:alicealicealicealiceali2') is None
    assert store.get('did:plc:bobbobbobbobbobbobbobbob') == {'other': 1}


def test_json_file_store_rejects_a_file_of_another_shape(tmp_path: Path) -> None:
    path = tmp_path / 'sessions.json'
    path.write_text('[]')

    with pytest.raises(ValueError, match='not a JSON object'):
        JsonFileStore(path).get('did:plc:alicealicealicealiceali2')


def test_secrets_are_not_in_repr() -> None:
    jwk = generate_p256_jwk()
    token_set = TokenSet(
        'https://auth.test',
        'did:plc:alicealicealicealiceali2',
        'https://pds.test',
        'atproto',
        'ACCESS',
        'DPoP',
        'REFRESH',
    )
    session = OAuthSessionData(jwk, AuthMethod('none'), token_set)
    state = OAuthStateData('https://auth.test', jwk, AuthMethod('none'), 'VERIFIER', 'http://127.0.0.1/', 1.0)

    response = TokenResponse('ACCESS', 'DPoP', 'atproto', 'did:plc:alicealicealicealiceali2', 'REFRESH')
    effect = call(print, 'ACCESS', token='REFRESH')

    for value in (token_set, session, state, response, effect):
        text = repr(value)
        assert 'ACCESS' not in text
        assert 'REFRESH' not in text
        assert 'VERIFIER' not in text
        assert jwk['d'] not in text


def test_memory_store_drops_expired_values_it_is_never_asked_for() -> None:
    store: MemoryStore[str] = MemoryStore(ttl=0.05)
    for index in range(100):
        store.set(f'key-{index}', 'value')

    time.sleep(0.1)
    store.set('fresh', 'value')

    assert list(store._values) == ['fresh']


@pytest.mark.parametrize(
    'client_id',
    [
        'https://app.example.com/client-metadata.json',
        'https://app.example.com/oauth/client-metadata.json?v=2',
        'https://xn--bcher-kva.example/a%2Fb',
        'https://app.example.com/a//b',
        'http://localhost',
        'http://localhost/',
        'http://localhost?scope=atproto+repo%3Aa.b.c%3Faction%3Dcreate',
        'http://localhost/?redirect_uri=http%3A%2F%2F127.0.0.1%3A8080%2Fcallback&redirect_uri=http%3A%2F%2F%5B%3A%3A1%5D%2F',
    ],
)
def test_valid_client_ids(client_id: str) -> None:
    redirect_uri = 'http://127.0.0.1/' if client_id.startswith('http:') else REDIRECT_URI

    assert build_client_metadata(client_id, [redirect_uri], 'atproto')['client_id'] == client_id


@pytest.mark.parametrize(
    'scope',
    [
        '',
        'transition:generic',
        'atproto  transition:generic',
        ' atproto',
        'atproto ',
        'atproto\ttransition:generic',
        'atproto "x"',
    ],
)
def test_malformed_scope_is_rejected(scope: str) -> None:
    with pytest.raises(ValueError, match='Scope must'):
        build_client_metadata(CLIENT_ID, [REDIRECT_URI], scope)


@pytest.mark.parametrize(
    ('issuer', 'valid'),
    [
        ('https://bsky.social', True),
        ('https://pds.example.com:8443', True),
        ('https://8.8.8.8', True),
        ('https://bsky.social/', False),
        ('https://bsky.social/path', False),
        ('https://bsky.social:443', False),
        ('https://bsky.social?x=1', False),
        ('https://user@bsky.social', False),
        ('https://localhost', False),
        ('https://127.0.0.1:8443', False),
        ('https://[::1]', False),
        ('https://intranet', False),
        ('https://printer.local', False),
        ('https://ex ample.com', False),
        ('http://bsky.social', False),
        ('HTTPS://bsky.social', False),
    ],
)
def test_issuer_identifier(issuer: str, valid: bool) -> None:
    metadata = {
        'issuer': issuer,
        'authorization_endpoint': 'https://bsky.social/oauth/authorize',
        'token_endpoint': 'https://bsky.social/oauth/token',
        'pushed_authorization_request_endpoint': 'https://bsky.social/oauth/par',
        'response_types_supported': ['code'],
        'grant_types_supported': ['authorization_code', 'refresh_token'],
        'code_challenge_methods_supported': ['S256'],
        'token_endpoint_auth_methods_supported': ['none', 'private_key_jwt'],
        'token_endpoint_auth_signing_alg_values_supported': ['ES256'],
        'scopes_supported': ['atproto'],
        'dpop_signing_alg_values_supported': ['ES256'],
        'authorization_response_iss_parameter_supported': True,
        'require_pushed_authorization_requests': True,
        'client_id_metadata_document_supported': True,
    }

    if valid:
        assert AuthServerMetadata.from_dict(metadata, issuer).issuer == issuer
    else:
        with pytest.raises(UnsupportedAuthServerError):
            AuthServerMetadata.from_dict(metadata, issuer)


def test_development_issuer_needs_allow_http() -> None:
    assert _is_origin('http://localhost:2583', allow_http=True)
    assert not _is_origin('http://localhost:2583', allow_http=False)
