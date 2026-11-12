import typing as t
from urllib.parse import parse_qsl, urlencode, urlsplit

import typing_extensions as te
from atproto_crypto.exceptions import InvalidJwkError
from atproto_crypto.jws import sign_jwt

from atproto_oauth.dpop import DpopKey, build_dpop_proof, generate_nonce
from atproto_oauth.exceptions import (
    AuthMethodUnsatisfiableError,
    OAuthCallbackError,
    OAuthError,
    OAuthResponseError,
    TokenRefreshError,
)
from atproto_oauth.keys import CLIENT_ASSERTION_ALG, Keyset
from atproto_oauth.metadata import ATPROTO_SCOPE, AuthServerMetadata, ClientMetadata
from atproto_oauth.models import (
    AUTH_METHOD_NONE,
    AUTH_METHOD_PRIVATE_KEY_JWT,
    AuthMethod,
    OAuthSessionData,
    OAuthStateData,
    TokenResponse,
    TokenSet,
)
from atproto_oauth.pkce import PKCE_METHOD
from atproto_oauth.resolver import ResolvedServer, is_atproto_did
from atproto_oauth.security import HttpResponse, get_origin

RefreshMode = t.Union[bool, te.Literal['auto']]

Json = t.Dict[str, t.Any]
Form = t.Dict[str, str]

CLIENT_ASSERTION_TYPE: t.Final = 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer'
_CLIENT_ASSERTION_LIFETIME: t.Final = 60

_STALE_LEEWAY: t.Final = 10.0
_STALE_JITTER: t.Final = 30.0

# parameters the client sets itself and a caller must not override
_RESERVED_PAR_PARAMS: t.Final = frozenset(
    {
        'client_id',
        'client_assertion',
        'client_assertion_type',
        'code_challenge',
        'code_challenge_method',
        'redirect_uri',
        'response_type',
        'scope',
        'state',
    }
)


def pick_redirect_uri(metadata: ClientMetadata, redirect_uri: t.Optional[str]) -> str:
    redirect_uris: t.List[str] = metadata['redirect_uris']
    if redirect_uri is None:
        return redirect_uris[0]

    if redirect_uri not in redirect_uris:
        raise ValueError(f'Redirect URI is not registered in the client metadata: {redirect_uri!r}')

    return redirect_uri


def pick_scope(metadata: ClientMetadata, scope: t.Optional[str]) -> str:
    registered: str = metadata['scope']
    if scope is None:
        return registered

    requested = scope.split(' ')
    if ATPROTO_SCOPE not in requested:
        raise ValueError(f'Scope must include "{ATPROTO_SCOPE}"')

    unknown = set(requested) - set(registered.split(' '))
    if unknown:
        raise ValueError(f'Scope is not registered in the client metadata: {" ".join(sorted(unknown))}')

    return scope


def negotiate_auth_method(server: AuthServerMetadata, metadata: ClientMetadata, keyset: Keyset) -> AuthMethod:
    """Choose how the client authenticates during a new session."""
    method: str = metadata['token_endpoint_auth_method']
    if method not in server.token_endpoint_auth_methods_supported:
        raise OAuthError(f'Authorization server {server.issuer!r} does not support the "{method}" authentication')

    if method == AUTH_METHOD_NONE:
        return AuthMethod(AUTH_METHOD_NONE)

    key = keyset.default
    if key is None:
        raise OAuthError('A confidential client requires at least one client authentication key')

    return AuthMethod(AUTH_METHOD_PRIVATE_KEY_JWT, key.kid)


def ensure_auth_method(server: AuthServerMetadata, auth_method: AuthMethod, keyset: Keyset) -> None:
    """Ensure the authentication method of an existing session can still be used.

    Raises:
        :class:`atproto_oauth.exceptions.AuthMethodUnsatisfiableError`: The method can not be used anymore.
    """
    if auth_method.method not in server.token_endpoint_auth_methods_supported:
        raise AuthMethodUnsatisfiableError(
            f'Authorization server {server.issuer!r} no longer supports the "{auth_method.method}" authentication'
        )

    if auth_method.method == AUTH_METHOD_PRIVATE_KEY_JWT and keyset.get(auth_method.kid) is None:
        raise AuthMethodUnsatisfiableError(f'Client authentication key "{auth_method.kid}" is no longer available')


def build_client_credentials(auth_method: AuthMethod, client_id: str, issuer: str, keyset: Keyset, now: float) -> Form:
    """Build the form fields that authenticate the client. The assertion is single-use."""
    if auth_method.method == AUTH_METHOD_NONE:
        return {'client_id': client_id}

    key = keyset.get(auth_method.kid)
    if key is None:
        raise AuthMethodUnsatisfiableError(f'Client authentication key "{auth_method.kid}" is no longer available')

    issued_at = int(now)
    assertion = sign_jwt(
        {'alg': CLIENT_ASSERTION_ALG, 'kid': key.kid},
        {
            'iss': client_id,
            'sub': client_id,
            'aud': issuer,
            'jti': generate_nonce(),
            'iat': issued_at,
            'exp': issued_at + _CLIENT_ASSERTION_LIFETIME,
        },
        key.private_key,
    )
    return {
        'client_id': client_id,
        'client_assertion_type': CLIENT_ASSERTION_TYPE,
        'client_assertion': assertion,
    }


def build_par_form(
    redirect_uri: str,
    scope: str,
    state: str,
    code_challenge: str,
    login_hint: t.Optional[str] = None,
    extra: t.Optional[t.Mapping[str, t.Any]] = None,
) -> Form:
    form: Form = {
        'response_type': 'code',
        'code_challenge': code_challenge,
        'code_challenge_method': PKCE_METHOD,
        'state': state,
        'redirect_uri': redirect_uri,
        'scope': scope,
    }
    if login_hint:
        form['login_hint'] = login_hint

    for name, value in (extra or {}).items():
        if name in _RESERVED_PAR_PARAMS:
            raise ValueError(f'Authorization request parameter "{name}" can not be overridden')

        if value is not None:
            form[name] = str(value)

    return form


def build_code_form(code: str, code_verifier: str, redirect_uri: str) -> Form:
    return {
        'grant_type': 'authorization_code',
        'code': code,
        'code_verifier': code_verifier,
        'redirect_uri': redirect_uri,
    }


def build_refresh_form(refresh_token: str) -> Form:
    return {'grant_type': 'refresh_token', 'refresh_token': refresh_token}


def build_revocation_form(token: str) -> Form:
    return {'token': token}


def build_authorization_url(server: AuthServerMetadata, client_id: str, request_uri: str) -> str:
    parts = urlsplit(server.authorization_endpoint)
    query = [*parse_qsl(parts.query, keep_blank_values=True), ('client_id', client_id), ('request_uri', request_uri)]
    return parts._replace(query=urlencode(query), fragment='').geturl()


def build_server_request(
    url: str, form: Form, credentials: Form, key: DpopKey, nonce: t.Optional[str]
) -> t.Dict[str, t.Any]:
    """Build the keyword arguments of a POST request to the authorization server."""
    return {
        'data': {**form, **credentials},
        'headers': {'DPoP': build_dpop_proof(key, 'POST', url, nonce), 'Accept': 'application/json'},
    }


def parse_server_response(response: HttpResponse) -> Json:
    """Decode a response of the authorization server.

    Raises:
        :class:`atproto_oauth.exceptions.OAuthResponseError`: The server answered with an error.
    """
    body = response.json()

    if 200 <= response.status_code < 300:
        if not isinstance(body, dict):
            raise OAuthResponseError(response.status_code, error_description='Response is not a JSON object')

        return body

    if isinstance(body, dict):
        error, description = body.get('error'), body.get('error_description')
        raise OAuthResponseError(
            response.status_code,
            error if isinstance(error, str) else None,
            description if isinstance(description, str) else None,
        )

    raise OAuthResponseError(response.status_code)


def parse_par_response(body: Json) -> str:
    request_uri = body.get('request_uri')
    if not isinstance(request_uri, str) or not request_uri:
        raise OAuthError('Authorization server did not return a "request_uri"')

    return request_uri


def parse_token_response(body: Json) -> TokenResponse:
    """Validate a token response against the AT Protocol OAuth profile."""
    access_token = body.get('access_token')
    if not isinstance(access_token, str) or not access_token:
        raise OAuthError('Token response has no "access_token"')

    if body.get('token_type') != 'DPoP':
        raise OAuthError('Token response must have the "DPoP" token type')

    sub = body.get('sub')
    if not isinstance(sub, str) or not is_atproto_did(sub):
        raise OAuthError('Token response must have an AT Protocol DID as "sub"')

    scope = body.get('scope')
    if not isinstance(scope, str) or ATPROTO_SCOPE not in scope.split(' '):
        raise OAuthError(f'Token response must grant the "{ATPROTO_SCOPE}" scope')

    if body.get('id_token') is not None:
        raise OAuthError('Token response must not have an "id_token"')

    refresh_token = body.get('refresh_token')
    if refresh_token is not None and not isinstance(refresh_token, str):
        raise OAuthError('Token response has an invalid "refresh_token"')

    expires_in = body.get('expires_in')
    if expires_in is not None and (isinstance(expires_in, bool) or not isinstance(expires_in, (int, float))):
        raise OAuthError('Token response has an invalid "expires_in"')

    return TokenResponse(
        access_token=access_token,
        token_type='DPoP',  # noqa: S106
        scope=scope,
        sub=sub,
        refresh_token=refresh_token or None,
        expires_in=expires_in,
    )


def make_token_set(response: TokenResponse, iss: str, aud: str, requested_at: float) -> TokenSet:
    """Build the tokens to store.

    Args:
        response: Validated token response.
        iss: Issuer the tokens came from.
        aud: URL of the account's PDS.
        requested_at: Time just before the token request was sent.
    """
    return TokenSet(
        iss=iss,
        sub=response.sub,
        aud=aud,
        scope=response.scope,
        access_token=response.access_token,
        token_type=response.token_type,
        refresh_token=response.refresh_token,
        expires_at=None if response.expires_in is None else requested_at + response.expires_in,
    )


def get_callback_state_key(params: t.Mapping[str, str]) -> str:
    if params.get('response') is not None:
        raise OAuthCallbackError('JARM responses are not supported', params)

    state = params.get('state')
    if not state:
        raise OAuthCallbackError('Callback has no "state" parameter', params)

    return state


def check_callback(
    params: t.Mapping[str, str], state: OAuthStateData, server: AuthServerMetadata, now: float, state_ttl: float
) -> str:
    """Validate the callback of an authorization request and return the authorization code."""
    if now - state.created_at > state_ttl:
        raise OAuthCallbackError('Authorization request expired', params, state.app_state)

    if params.get('error') is not None:
        description = params.get('error_description') or params['error']
        raise OAuthCallbackError(f'Authorization failed: {description}', params, state.app_state)

    code = params.get('code')
    if not code:
        raise OAuthCallbackError('Callback has no "code" parameter', params, state.app_state)

    # authorization_response_iss_parameter_supported is mandatory, so the parameter is always expected
    issuer = params.get('iss')
    if issuer is None:
        raise OAuthCallbackError('Callback has no "iss" parameter', params, state.app_state)

    if issuer != server.issuer or issuer != state.iss:
        raise OAuthCallbackError('Callback comes from another issuer', params, state.app_state)

    return code


def check_expected_sub(state: OAuthStateData, sub: str) -> None:
    if state.did is not None and state.did != sub:
        raise OAuthError(f'Authorized account {sub!r} is not the expected {state.did!r}')


def needs_refresh(
    token_set: TokenSet, refresh: RefreshMode, rejected: t.Optional[TokenSet], now: float, jitter: float
) -> bool:
    """Decide whether stored tokens must be refreshed before use.

    Args:
        token_set: Stored tokens.
        refresh: ``'auto'`` refreshes tokens that are about to expire, :obj:`True` always, :obj:`False` never.
        rejected: Tokens the resource server rejected, when that is why a refresh is forced.
        now: Current time.
        jitter: Random number between 0 and 1, so that processes started together do not refresh at the same moment.
    """
    if refresh is False:
        return False

    if refresh == 'auto':
        if token_set.expires_at is None:
            return False

        return token_set.expires_at < now + _STALE_LEEWAY + _STALE_JITTER * jitter

    # someone else already replaced the tokens the server rejected
    return rejected is None or token_set.access_token == rejected.access_token


def is_invalid_grant(error: OAuthResponseError) -> bool:
    return error.status_code == 400 and error.error == 'invalid_grant'


def build_state_data(
    server: AuthServerMetadata,
    resolved: ResolvedServer,
    dpop_jwk: t.Dict[str, t.Any],
    auth_method: AuthMethod,
    pkce_verifier: str,
    redirect_uri: str,
    app_state: t.Optional[str],
    now: float,
) -> OAuthStateData:
    return OAuthStateData(
        iss=server.issuer,
        dpop_jwk=dpop_jwk,
        auth_method=auth_method,
        pkce_verifier=pkce_verifier,
        redirect_uri=redirect_uri,
        created_at=now,
        did=resolved.identity.did if resolved.identity else None,
        app_state=app_state,
    )


def build_session_data(
    dpop_jwk: t.Dict[str, t.Any],
    auth_method: AuthMethod,
    response: TokenResponse,
    issuer: str,
    pds: str,
    requested_at: float,
) -> OAuthSessionData:
    return OAuthSessionData(
        dpop_jwk=dpop_jwk,
        auth_method=auth_method,
        token_set=make_token_set(response, issuer, pds, requested_at),
    )


def get_verified_pds(resolved: ResolvedServer, issuer: str) -> t.Optional[str]:
    """Return the origin of the account's PDS when the authorization server is the one that serves the account."""
    if resolved.server.issuer != issuer or resolved.identity is None:
        return None

    return get_origin(resolved.identity.pds)


def load_session_data(did: str, value: t.Any) -> OAuthSessionData:
    """Validate what a session store returned.

    Raises:
        :class:`atproto_oauth.exceptions.TokenRefreshError`: The stored value is not a session of the account.
    """
    try:
        data = value if isinstance(value, OAuthSessionData) else OAuthSessionData.from_dict(value)
        DpopKey(data.dpop_jwk)
        get_origin(data.token_set.aud)
    except (ValueError, TypeError, AttributeError, InvalidJwkError) as e:
        raise TokenRefreshError(did, f'Stored session is invalid: {e}') from e

    if data.token_set.sub != did:
        raise TokenRefreshError(did, 'Stored session belongs to another account')

    return data


def load_state_data(params: t.Mapping[str, str], value: t.Any) -> OAuthStateData:
    try:
        state = value if isinstance(value, OAuthStateData) else OAuthStateData.from_dict(value)
        DpopKey(state.dpop_jwk)
    except (ValueError, TypeError, AttributeError, InvalidJwkError) as e:
        raise OAuthCallbackError(f'Stored authorization request is invalid: {e}', params) from e

    return state


def as_callback_error(error: OAuthError, params: t.Mapping[str, str], app_state: t.Optional[str]) -> OAuthCallbackError:
    if isinstance(error, OAuthCallbackError):
        return error

    return OAuthCallbackError(str(error), params, app_state)
