"""In-process PDS and authorization server for OAuth tests, served through ``httpx.MockTransport``."""

import dataclasses
import hashlib
import json
import secrets
import time
import typing as t
from dataclasses import dataclass, field
from urllib.parse import parse_qs, urlsplit

import httpx
from atproto_crypto.algs import P256
from atproto_crypto.jwk import base64url_decode, base64url_encode, get_jwk_thumbprint, load_public_jwk
from atproto_identity.did.atproto_data import AtprotoData
from atproto_identity.exceptions import DidNotFoundError
from atproto_oauth import OAuthSessionData
from cryptography.hazmat.primitives import serialization

if t.TYPE_CHECKING:
    from atproto_identity.resolver import AsyncIdResolver, IdResolver

ISSUER = 'https://auth.test'
PDS = 'https://pds.test'
DID = 'did:plc:alicealicealicealiceali2'
BOB_DID = 'did:plc:bobbobbobbobbobbobbobbob'
VICTIM_DID = 'did:plc:victimvictimvictimvictim'
UNKNOWN_DID = 'did:plc:unknownunknownunknownunk'
HANDLE = 'alice.test'

_P256 = P256()


def decode_jwt(jwt: str) -> t.Tuple[t.Dict[str, t.Any], t.Dict[str, t.Any]]:
    header, payload, _ = jwt.split('.')
    return json.loads(base64url_decode(header)), json.loads(base64url_decode(payload))


def verify_jwt(jwt: str, jwk: t.Mapping[str, t.Any]) -> bool:
    """Verify with the verifier of the SDK, which also rejects high-S signatures."""
    signing_input, signature = jwt.rsplit('.', 1)
    public_key = load_public_jwk(jwk).public_bytes(
        serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint
    )
    return _P256.verify_signature(public_key, signing_input.encode(), base64url_decode(signature))


def _json(status_code: int, body: t.Any, headers: t.Optional[t.Dict[str, str]] = None) -> httpx.Response:
    return httpx.Response(status_code, json=body, headers=headers)


def _error(
    status_code: int, error: str, description: str = '', headers: t.Optional[t.Dict[str, str]] = None
) -> httpx.Response:
    return _json(status_code, {'error': error, 'error_description': description or error}, headers)


@dataclass
class _Grant:
    sub: str
    scope: str
    jkt: str
    client_id: str
    access_token: str = ''
    refresh_token: t.Optional[str] = None
    revoked: bool = False


@dataclass
class _DpopProof:
    jkt: str
    payload: t.Dict[str, t.Any]


@dataclass
class Account:
    did: str = DID
    handle: t.Optional[str] = HANDLE
    pds: t.Optional[str] = PDS


class _DpopError(Exception):
    def __init__(self, error: str, description: str = '') -> None:
        super().__init__(description or error)
        self.error = error


@dataclass
class FakeServer:
    """PDS at ``https://pds.test`` and authorization server at ``https://auth.test``."""

    client_jwks: t.Optional[t.Dict[str, t.Any]] = None
    expires_in: t.Optional[int] = 3600
    issue_refresh_tokens: bool = True
    as_nonce: str = 'as-nonce-1'
    pds_nonce: str = 'pds-nonce-1'
    #: Overrides merged into the metadata documents and the token responses.
    server_metadata_overrides: t.Dict[str, t.Any] = field(default_factory=dict)
    resource_metadata_overrides: t.Dict[str, t.Any] = field(default_factory=dict)
    token_response_overrides: t.Dict[str, t.Any] = field(default_factory=dict)
    #: Path -> response, to make an endpoint fail.
    forced_responses: t.Dict[str, httpx.Response] = field(default_factory=dict)
    accounts: t.Dict[str, Account] = field(default_factory=lambda: {DID: Account()})
    #: Handle -> DID of handles that resolve to a DID whose document does not list them.
    handle_aliases: t.Dict[str, str] = field(default_factory=dict)
    #: Make the PDS reject access tokens right after they are issued.
    reject_new_access_tokens: bool = False

    def __post_init__(self) -> None:
        self.requests: t.List[httpx.Request] = []
        self.log: t.List[t.Tuple[str, str, int]] = []
        self.par_requests: t.Dict[str, t.Dict[str, str]] = {}
        self.codes: t.Dict[str, t.Dict[str, str]] = {}
        self.grants: t.List[_Grant] = []
        self.revoked_tokens: t.List[str] = []
        self.seen_jtis: t.Set[str] = set()
        self.bodies: t.List[bytes] = []
        self._counter = 0

    @property
    def transport(self) -> httpx.MockTransport:
        return httpx.MockTransport(self.handle)

    def count(self, path: str) -> int:
        return sum(1 for _, logged_path, _ in self.log if logged_path == path)

    def statuses(self, path: str) -> t.List[int]:
        return [status for _, logged_path, status in self.log if logged_path == path]

    def _token(self, kind: str) -> str:
        self._counter += 1
        return f'{kind}-{self._counter}-{secrets.token_hex(4)}'

    def approve(self, authorization_url: str, sub: str = DID) -> t.Dict[str, str]:
        """Act as the user approving the request. Returns the query parameters of the redirect back."""
        parts = urlsplit(authorization_url)
        assert f'{parts.scheme}://{parts.netloc}{parts.path}' == f'{ISSUER}/oauth/authorize'
        query = {name: values[0] for name, values in parse_qs(parts.query).items()}
        request = self.par_requests.pop(query['request_uri'])
        assert query['client_id'] == request['client_id']

        code = self._token('code')
        self.codes[code] = {**request, 'sub': sub}
        return {'code': code, 'state': request['state'], 'iss': ISSUER}

    def deny(self, authorization_url: str) -> t.Dict[str, str]:
        query = {name: values[0] for name, values in parse_qs(urlsplit(authorization_url).query).items()}
        request = self.par_requests.pop(query['request_uri'])
        return {
            'error': 'access_denied',
            'error_description': 'The user denied the request',
            'state': request['state'],
            'iss': ISSUER,
        }

    def expire_access_tokens(self) -> None:
        """Make the PDS reject every access token issued so far."""
        for grant in self.grants:
            grant.access_token = ''

    def handle(self, request: httpx.Request) -> httpx.Response:
        request.read()
        self.requests.append(request)

        response = self.forced_responses.get(request.url.path) or self._dispatch(request)
        self.log.append((request.method, request.url.path, response.status_code))
        return response

    def _dispatch(self, request: httpx.Request) -> httpx.Response:
        origin = f'{request.url.scheme}://{request.url.host}'
        path = request.url.path

        if origin == PDS:
            if path == '/.well-known/oauth-protected-resource':
                return _json(
                    200, {'resource': PDS, 'authorization_servers': [ISSUER], **self.resource_metadata_overrides}
                )

            if path.startswith('/xrpc/'):
                return self._xrpc(request)
        elif origin == ISSUER:
            if path == '/.well-known/oauth-authorization-server':
                return _json(200, self.server_metadata)

            if path in {'/oauth/par', '/oauth/token', '/oauth/revoke'}:
                return self._auth_server_endpoint(request)

        return httpx.Response(404, json={'error': 'NotFound'})

    @property
    def server_metadata(self) -> t.Dict[str, t.Any]:
        return {
            'issuer': ISSUER,
            'authorization_endpoint': f'{ISSUER}/oauth/authorize',
            'token_endpoint': f'{ISSUER}/oauth/token',
            'pushed_authorization_request_endpoint': f'{ISSUER}/oauth/par',
            'revocation_endpoint': f'{ISSUER}/oauth/revoke',
            'response_types_supported': ['code'],
            'grant_types_supported': ['authorization_code', 'refresh_token'],
            'code_challenge_methods_supported': ['S256'],
            'token_endpoint_auth_methods_supported': ['none', 'private_key_jwt'],
            'token_endpoint_auth_signing_alg_values_supported': ['ES256', 'ES256K'],
            'scopes_supported': ['atproto', 'transition:generic'],
            'dpop_signing_alg_values_supported': ['ES256', 'ES256K'],
            'authorization_response_iss_parameter_supported': True,
            'require_pushed_authorization_requests': True,
            'client_id_metadata_document_supported': True,
            'protected_resources': [PDS],
            **self.server_metadata_overrides,
        }

    def _check_dpop(  # noqa: C901
        self, request: httpx.Request, nonce: str, access_token: t.Optional[str] = None
    ) -> _DpopProof:
        proof = request.headers.get('dpop')
        if not proof:
            raise _DpopError('invalid_dpop_proof', 'DPoP proof required')

        header, payload = decode_jwt(proof)
        if header.get('typ') != 'dpop+jwt' or header.get('alg') != 'ES256':
            raise _DpopError('invalid_dpop_proof', 'Unexpected proof header')

        if 'd' in header['jwk'] or 'kid' in header['jwk']:
            raise _DpopError('invalid_dpop_proof', 'Proof must embed a bare public key')

        if not verify_jwt(proof, header['jwk']):
            raise _DpopError('invalid_dpop_proof', 'Bad proof signature')

        htu = str(request.url.copy_with(query=None, fragment=None))
        if payload.get('htm') != request.method or payload.get('htu') != htu:
            raise _DpopError('invalid_dpop_proof', f'htm/htu mismatch: {payload.get("htu")} != {htu}')

        if abs(time.time() - payload.get('iat', 0)) > 60:
            raise _DpopError('invalid_dpop_proof', 'Stale proof')

        if 'exp' in payload:
            raise _DpopError('invalid_dpop_proof', 'Unexpected exp claim')

        jti = payload.get('jti')
        if not jti or jti in self.seen_jtis:
            raise _DpopError('invalid_dpop_proof', 'jti missing or replayed')

        self.seen_jtis.add(jti)

        if payload.get('nonce') != nonce:
            raise _DpopError('use_dpop_nonce', 'Authorization server requires nonce in DPoP proof')

        expected_ath = None
        if access_token is not None:
            expected_ath = base64url_encode(hashlib.sha256(access_token.encode()).digest())

        if payload.get('ath') != expected_ath:
            raise _DpopError('invalid_dpop_proof', 'ath mismatch')

        return _DpopProof(get_jwk_thumbprint(header['jwk']), payload)

    def _check_client(self, form: t.Dict[str, str]) -> t.Optional[httpx.Response]:  # noqa: C901
        client_id = form.get('client_id')
        if not client_id:
            return _error(400, 'invalid_request', 'client_id is required')

        assertion = form.get('client_assertion')
        if self.client_jwks is None:
            if assertion is not None:
                return _error(400, 'invalid_client', 'Unexpected client assertion')

            return None

        if form.get('client_assertion_type') != 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer':
            return _error(401, 'invalid_client', 'client_assertion_type is required')

        if not assertion:
            return _error(401, 'invalid_client', 'client_assertion is required')

        header, payload = decode_jwt(assertion)
        key = next((k for k in self.client_jwks['keys'] if k.get('kid') == header.get('kid')), None)
        if key is None or 'd' in key:
            return _error(401, 'invalid_client', f'Unknown key {header.get("kid")}')

        if header.get('alg') != 'ES256' or not verify_jwt(assertion, key):
            return _error(401, 'invalid_client', 'Bad assertion signature')

        if payload.get('iss') != client_id or payload.get('sub') != client_id or payload.get('aud') != ISSUER:
            return _error(401, 'invalid_client', 'Bad assertion claims')

        if not payload.get('jti') or payload['jti'] in self.seen_jtis:
            return _error(401, 'invalid_client', 'Assertion jti missing or replayed')

        self.seen_jtis.add(payload['jti'])
        now = time.time()
        if not (payload.get('iat', 0) <= now + 5 and now < payload.get('exp', 0) <= now + 120):
            return _error(401, 'invalid_client', 'Assertion expired')

        form['_kid'] = header['kid']
        return None

    def _auth_server_endpoint(self, request: httpx.Request) -> httpx.Response:
        headers = {'DPoP-Nonce': self.as_nonce}
        if request.method != 'POST' or 'application/x-www-form-urlencoded' not in request.headers['content-type']:
            return _error(400, 'invalid_request', 'Form POST required', headers)

        form = {name: values[0] for name, values in parse_qs(request.content.decode()).items()}

        try:
            proof = self._check_dpop(request, self.as_nonce)
        except _DpopError as e:
            return _error(400, e.error, str(e), headers)

        client_error = self._check_client(form)
        if client_error is not None:
            return client_error

        path = request.url.path
        if path == '/oauth/par':
            response = self._par(form, proof)
        elif path == '/oauth/token':
            response = self._issue_tokens(form, proof)
        else:
            response = self._revoke(form)

        response.headers['DPoP-Nonce'] = self.as_nonce
        return response

    def _par(self, form: t.Dict[str, str], proof: _DpopProof) -> httpx.Response:
        required = ('response_type', 'code_challenge', 'code_challenge_method', 'state', 'redirect_uri', 'scope')
        missing = [name for name in required if not form.get(name)]
        if missing:
            return _error(400, 'invalid_request', f'Missing {missing}')

        if form['response_type'] != 'code' or form['code_challenge_method'] != 'S256':
            return _error(400, 'invalid_request', 'Unsupported response type or challenge method')

        if 'atproto' not in form['scope'].split(' '):
            return _error(400, 'invalid_scope', 'atproto scope is required')

        request_uri = f'urn:ietf:params:oauth:request_uri:{self._token("req")}'
        self.par_requests[request_uri] = {**form, 'jkt': proof.jkt}
        return _json(201, {'request_uri': request_uri, 'expires_in': 300})

    def _issue_tokens(self, form: t.Dict[str, str], proof: _DpopProof) -> httpx.Response:  # noqa: C901
        grant_type = form.get('grant_type')

        if grant_type == 'authorization_code':
            request = self.codes.pop(form.get('code', ''), None)
            if request is None:
                return _error(400, 'invalid_grant', 'Invalid code')

            challenge = base64url_encode(hashlib.sha256(form.get('code_verifier', '').encode()).digest())
            if challenge != request['code_challenge']:
                return _error(400, 'invalid_grant', 'Invalid code_verifier')

            if form.get('redirect_uri') != request['redirect_uri'] or form['client_id'] != request['client_id']:
                return _error(400, 'invalid_grant', 'redirect_uri or client_id mismatch')

            if proof.jkt != request['jkt']:
                return _error(400, 'invalid_dpop_proof', 'DPoP key mismatch')

            grant = _Grant(request['sub'], request['scope'], proof.jkt, form['client_id'])
            self.grants.append(grant)
        elif grant_type == 'refresh_token':
            refresh_token = form.get('refresh_token')
            grant = next((g for g in self.grants if refresh_token and g.refresh_token == refresh_token), None)
            if grant is None or grant.revoked:
                return _error(400, 'invalid_grant', 'Invalid refresh token')

            if proof.jkt != grant.jkt or form['client_id'] != grant.client_id:
                return _error(400, 'invalid_grant', 'DPoP key or client mismatch')
        else:
            return _error(400, 'unsupported_grant_type')

        grant.access_token = self._token('access')
        grant.refresh_token = self._token('refresh') if self.issue_refresh_tokens else None

        body: t.Dict[str, t.Any] = {
            'access_token': grant.access_token,
            'token_type': 'DPoP',
            'scope': grant.scope,
            'sub': grant.sub,
        }
        if grant.refresh_token:
            body['refresh_token'] = grant.refresh_token

        if self.expires_in is not None:
            body['expires_in'] = self.expires_in

        body.update(self.token_response_overrides)
        if self.reject_new_access_tokens:
            grant.access_token = ''

        return _json(200, {name: value for name, value in body.items() if value is not None})

    def _revoke(self, form: t.Dict[str, str]) -> httpx.Response:
        token = form.get('token', '')
        self.revoked_tokens.append(token)
        for grant in self.grants:
            if token in {grant.access_token, grant.refresh_token}:
                grant.revoked = True
                grant.access_token = ''
                grant.refresh_token = None

        return httpx.Response(200)

    def _xrpc(self, request: httpx.Request) -> httpx.Response:
        headers = {'DPoP-Nonce': self.pds_nonce}

        def unauthorized(error: str, description: str = '') -> httpx.Response:
            www = f'DPoP error="{error}", error_description="{description or error}"'
            return _json(401, {'error': error, 'message': description or error}, {**headers, 'WWW-Authenticate': www})

        authorization = request.headers.get('authorization', '')
        if authorization.startswith('Bearer '):
            return _json(200, {'bearer': authorization[7:]}, headers)

        if not authorization.startswith('DPoP '):
            return _json(401, {'error': 'AuthMissing', 'message': 'Authentication Required'}, headers)

        token = authorization[5:]
        try:
            proof = self._check_dpop(request, self.pds_nonce, token)
        except _DpopError as e:
            return unauthorized(e.error, str(e))

        grant = next((g for g in self.grants if g.access_token and g.access_token == token), None)
        if grant is None:
            return unauthorized('invalid_token', 'Token expired or revoked')

        if grant.jkt != proof.jkt:
            return unauthorized('invalid_token', 'DPoP key mismatch')

        self.bodies.append(request.content)
        nsid = request.url.path[len('/xrpc/') :]
        if nsid == 'app.bsky.actor.getProfile':
            return _json(
                200, {'did': grant.sub, 'handle': self.accounts[grant.sub].handle or 'handle.invalid'}, headers
            )

        if nsid == 'com.atproto.repo.createRecord':
            record = json.loads(request.content)
            return _json(
                200,
                {
                    'uri': f'at://{record["repo"]}/{record["collection"]}/3kabc',
                    'cid': 'bafyreidfayvfuwqa7qlnopdjiqrxzs6blmoeu4rujcjtnci5beludirz2a',
                },
                headers,
            )

        return _json(200, {'nsid': nsid, 'sub': grant.sub, 'size': len(request.content)}, headers)


def _resolve_handle(server: FakeServer, handle: str) -> t.Optional[str]:
    if handle in server.handle_aliases:
        return server.handle_aliases[handle]

    return next((account.did for account in server.accounts.values() if account.handle == handle), None)


def _resolve_atproto_data(server: FakeServer, did: str) -> AtprotoData:
    account = server.accounts.get(did)
    if account is None:
        raise DidNotFoundError(did)

    return AtprotoData(did=account.did, handle=account.handle, pds=account.pds)


class _FakeHandleResolver:
    def __init__(self, server: FakeServer) -> None:
        self._server = server

    def resolve(self, handle: str) -> t.Optional[str]:
        return _resolve_handle(self._server, handle)


class _FakeDidResolver:
    def __init__(self, server: FakeServer) -> None:
        self._server = server
        self.calls: t.List[t.Tuple[str, bool]] = []

    def resolve_atproto_data(self, did: str, force_refresh: bool = False) -> AtprotoData:
        self.calls.append((did, force_refresh))
        return _resolve_atproto_data(self._server, did)


class FakeIdResolver:
    def __init__(self, server: FakeServer) -> None:
        self.handle = _FakeHandleResolver(server)
        self.did = _FakeDidResolver(server)


class _AsyncFakeHandleResolver:
    def __init__(self, server: FakeServer) -> None:
        self._server = server

    async def resolve(self, handle: str) -> t.Optional[str]:
        return _resolve_handle(self._server, handle)


class _AsyncFakeDidResolver:
    def __init__(self, server: FakeServer) -> None:
        self._server = server
        self.calls: t.List[t.Tuple[str, bool]] = []

    async def resolve_atproto_data(self, did: str, force_refresh: bool = False) -> AtprotoData:
        self.calls.append((did, force_refresh))
        return _resolve_atproto_data(self._server, did)


class AsyncFakeIdResolver:
    def __init__(self, server: FakeServer) -> None:
        self.handle = _AsyncFakeHandleResolver(server)
        self.did = _AsyncFakeDidResolver(server)


def fake_id_resolver(server: FakeServer) -> 'IdResolver':
    return t.cast('IdResolver', FakeIdResolver(server))


def async_fake_id_resolver(server: FakeServer) -> 'AsyncIdResolver':
    return t.cast('AsyncIdResolver', AsyncFakeIdResolver(server))


def get_stored_session(store: t.Any, did: str = DID) -> OAuthSessionData:
    data = store.get(did)
    assert isinstance(data, OAuthSessionData)
    return data


def make_stale(data: OAuthSessionData) -> OAuthSessionData:
    """Return the session with an access token that expired."""
    return dataclasses.replace(data, token_set=dataclasses.replace(data.token_set, expires_at=time.time() - 1))


def record_causes(causes: t.List[BaseException]) -> t.Callable[[str, BaseException], None]:
    def callback(did: str, cause: BaseException) -> None:
        causes.append(cause)

    return callback


def record_deletions(deleted: t.List[t.Tuple[str, BaseException]]) -> t.Callable[[str, BaseException], None]:
    def callback(did: str, cause: BaseException) -> None:
        deleted.append((did, cause))

    return callback


def record_access_tokens(tokens: t.List[str]) -> t.Callable[[str, OAuthSessionData], None]:
    def callback(did: str, data: OAuthSessionData) -> None:
        tokens.append(data.token_set.access_token)

    return callback
