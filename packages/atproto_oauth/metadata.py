import ipaddress
import re
import typing as t
from dataclasses import dataclass, field
from urllib.parse import parse_qsl, urlencode, urlsplit

from atproto_oauth.dpop import DPOP_ALG
from atproto_oauth.exceptions import OAuthResolverError, UnsupportedAuthServerError
from atproto_oauth.keys import CLIENT_ASSERTION_ALG, Keyset
from atproto_oauth.models import AUTH_METHOD_NONE, AUTH_METHOD_PRIVATE_KEY_JWT
from atproto_oauth.security import get_origin

ClientMetadata = t.Dict[str, t.Any]

ATPROTO_SCOPE: t.Final = 'atproto'

LOOPBACK_CLIENT_ID_ORIGIN: t.Final = 'http://localhost'
DEFAULT_LOOPBACK_REDIRECT_URIS: t.Final = ('http://127.0.0.1/', 'http://[::1]/')
_LOOPBACK_REDIRECT_HOSTS: t.Final = frozenset({'127.0.0.1', '::1'})

_SUPPORTED_AUTH_METHODS: t.Final = frozenset({AUTH_METHOD_NONE, AUTH_METHOD_PRIVATE_KEY_JWT})

_DOMAIN: t.Final = re.compile(r'[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+')
_LOOPBACK_HOSTS: t.Final = frozenset({'localhost', '127.0.0.1', '[::1]'})
# what a URL parser leaves untouched, so that the value is its own canonical form
_CANONICAL_PATH: t.Final = re.compile(r"(?:/(?:[A-Za-z0-9._~!$&'()*+,;=:@-]|%[0-9A-Fa-f]{2})*)+")
_CANONICAL_QUERY: t.Final = re.compile(r"(?:[A-Za-z0-9._~!$&'()*+,;=:@/?-]|%[0-9A-Fa-f]{2})*")
_DOT_SEGMENT: t.Final = re.compile(r'/(?:\.|%2e){1,2}(?=/|$)', re.IGNORECASE)
# scope-token of RFC 6749: printable ASCII without the double quote and the backslash
_SCOPE: t.Final = re.compile(r'[\x21\x23-\x5B\x5D-\x7E]+(?: [\x21\x23-\x5B\x5D-\x7E]+)*')


def _is_ip(hostname: str) -> bool:
    try:
        ipaddress.ip_address(hostname)
    except ValueError:
        return False

    return True


def _is_public_domain(hostname: str) -> bool:
    return bool(_DOMAIN.fullmatch(hostname)) and not hostname.endswith('.local') and not _is_ip(hostname)


def _is_origin(url: t.Any, allow_http: bool) -> bool:
    """Tell whether a value is the origin of a server, written the way a URL parser would write it."""
    if not isinstance(url, str):
        return False

    try:
        origin = get_origin(url)
        parts = urlsplit(url)
    except ValueError:
        return False

    if url != origin:
        return False

    if allow_http:
        return parts.scheme in {'https', 'http'}

    hostname = parts.hostname or ''
    if parts.scheme != 'https' or hostname == 'localhost':
        return False

    if _is_ip(hostname):
        return not ipaddress.ip_address(hostname).is_loopback

    return _is_public_domain(hostname)


def _is_endpoint(url: t.Any, allow_http: bool) -> bool:
    if not isinstance(url, str):
        return False

    try:
        parts = urlsplit(url)
        _ = parts.port
    except ValueError:
        return False

    return bool(parts.hostname) and (parts.scheme == 'https' or (allow_http and parts.scheme == 'http'))


def _string_list(data: t.Mapping[str, t.Any], name: str) -> t.List[str]:
    value = data.get(name)
    if not isinstance(value, list):
        return []

    return [item for item in t.cast('t.List[t.Any]', value) if isinstance(item, str)]


@dataclass(frozen=True)
class AuthServerMetadata:
    """Metadata of an authorization server that follows the AT Protocol OAuth profile.

    Attributes:
        raw: The whole metadata document.
    """

    issuer: str
    authorization_endpoint: str
    token_endpoint: str
    pushed_authorization_request_endpoint: str
    revocation_endpoint: t.Optional[str] = None
    token_endpoint_auth_methods_supported: t.Tuple[str, ...] = ()
    protected_resources: t.Optional[t.Tuple[str, ...]] = None
    raw: t.Dict[str, t.Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, data: t.Any, issuer: str, allow_http: bool = False) -> 'AuthServerMetadata':
        """Validate a metadata document.

        Args:
            data: Decoded metadata document.
            issuer: Issuer the document was requested for.
            allow_http: Accept ``http`` URLs. For development environments.

        Raises:
            :class:`atproto_oauth.exceptions.UnsupportedAuthServerError`: The server can not be used.
        """
        if not isinstance(data, dict):
            raise UnsupportedAuthServerError('Authorization server metadata is not a JSON object')

        metadata = t.cast('t.Dict[str, t.Any]', data)
        for requirement, satisfied in _get_auth_server_requirements(metadata, issuer, allow_http):
            if not satisfied:
                raise UnsupportedAuthServerError(f'Authorization server {issuer!r}: {requirement}')

        protected_resources = metadata.get('protected_resources')
        return cls(
            issuer=metadata['issuer'],
            authorization_endpoint=metadata['authorization_endpoint'],
            token_endpoint=metadata['token_endpoint'],
            pushed_authorization_request_endpoint=metadata['pushed_authorization_request_endpoint'],
            revocation_endpoint=metadata.get('revocation_endpoint'),
            token_endpoint_auth_methods_supported=tuple(
                _string_list(metadata, 'token_endpoint_auth_methods_supported')
            ),
            protected_resources=(
                tuple(_string_list(metadata, 'protected_resources')) if isinstance(protected_resources, list) else None
            ),
            raw=metadata,
        )


def _get_auth_server_requirements(
    data: t.Mapping[str, t.Any], issuer: str, allow_http: bool
) -> t.List[t.Tuple[str, bool]]:
    auth_methods = _string_list(data, 'token_endpoint_auth_methods_supported')
    auth_algs = _string_list(data, 'token_endpoint_auth_signing_alg_values_supported')
    grant_types = _string_list(data, 'grant_types_supported')
    revocation_endpoint = data.get('revocation_endpoint')

    return [
        ('"issuer" must be an origin', _is_origin(data.get('issuer'), allow_http)),
        ('"issuer" must match the requested issuer', data.get('issuer') == issuer),
        ('"authorization_endpoint" is required', _is_endpoint(data.get('authorization_endpoint'), allow_http)),
        ('"token_endpoint" is required', _is_endpoint(data.get('token_endpoint'), allow_http)),
        (
            '"pushed_authorization_request_endpoint" is required',
            _is_endpoint(data.get('pushed_authorization_request_endpoint'), allow_http),
        ),
        (
            '"revocation_endpoint" must be a URL',
            revocation_endpoint is None or _is_endpoint(revocation_endpoint, allow_http),
        ),
        ('"response_types_supported" must include "code"', 'code' in _string_list(data, 'response_types_supported')),
        ('"grant_types_supported" must include "authorization_code"', 'authorization_code' in grant_types),
        ('"grant_types_supported" must include "refresh_token"', 'refresh_token' in grant_types),
        (
            '"code_challenge_methods_supported" must include "S256"',
            'S256' in _string_list(data, 'code_challenge_methods_supported'),
        ),
        ('"token_endpoint_auth_methods_supported" must include "none"', AUTH_METHOD_NONE in auth_methods),
        (
            '"token_endpoint_auth_methods_supported" must include "private_key_jwt"',
            AUTH_METHOD_PRIVATE_KEY_JWT in auth_methods,
        ),
        (
            '"token_endpoint_auth_signing_alg_values_supported" must include "ES256"',
            CLIENT_ASSERTION_ALG in auth_algs,
        ),
        ('"token_endpoint_auth_signing_alg_values_supported" must not include "none"', 'none' not in auth_algs),
        ('"scopes_supported" must include "atproto"', ATPROTO_SCOPE in _string_list(data, 'scopes_supported')),
        (
            '"dpop_signing_alg_values_supported" must include "ES256"',
            DPOP_ALG in _string_list(data, 'dpop_signing_alg_values_supported'),
        ),
        (
            '"authorization_response_iss_parameter_supported" must be true',
            data.get('authorization_response_iss_parameter_supported') is True,
        ),
        (
            '"require_pushed_authorization_requests" must be true',
            data.get('require_pushed_authorization_requests') is True,
        ),
        (
            '"client_id_metadata_document_supported" must be true',
            data.get('client_id_metadata_document_supported') is True,
        ),
        (
            '"require_request_uri_registration" must not be false',
            data.get('require_request_uri_registration') is not False,
        ),
    ]


def get_issuer_from_protected_resource_metadata(data: t.Any, origin: str, allow_http: bool = False) -> str:
    """Validate protected resource metadata of a PDS and return the issuer of its authorization server.

    Args:
        data: Decoded metadata document.
        origin: Origin of the PDS the document was requested from.
        allow_http: Accept ``http`` URLs. For development environments.

    Raises:
        :class:`atproto_oauth.exceptions.OAuthResolverError`: The document is invalid.
    """
    if not isinstance(data, dict):
        raise OAuthResolverError(f'Protected resource metadata of {origin!r} is not a JSON object')

    if data.get('resource') != origin:
        raise OAuthResolverError(f'Protected resource metadata of {origin!r} describes another resource')

    servers = data.get('authorization_servers')
    if not isinstance(servers, list) or len(servers) != 1:
        raise OAuthResolverError(f'{origin!r} must declare exactly one authorization server')

    issuer: t.Any = servers[0]
    if not isinstance(issuer, str) or not _is_origin(issuer, allow_http):
        raise OAuthResolverError(f'Authorization server of {origin!r} is not an origin: {issuer!r}')

    return issuer


def _parse_query(url: str) -> t.List[t.Tuple[str, str]]:
    return parse_qsl(urlsplit(url).query, keep_blank_values=True)


def is_loopback_redirect_uri(redirect_uri: str) -> bool:
    if not redirect_uri.startswith('http://'):
        return False

    try:
        parts = urlsplit(redirect_uri)
        _ = parts.port
    except ValueError:
        return False

    credentials = parts.username is not None or parts.password is not None
    return parts.hostname in _LOOPBACK_REDIRECT_HOSTS and not parts.fragment and not credentials


def get_redirect_uri_without_port(redirect_uri: str) -> str:
    parts = urlsplit(redirect_uri)
    hostname = f'[{parts.hostname}]' if ':' in (parts.hostname or '') else parts.hostname
    return parts._replace(netloc=hostname or '').geturl()


def build_loopback_client_id(redirect_uris: t.Optional[t.Sequence[str]] = None, scope: t.Optional[str] = None) -> str:
    """Build the ``client_id`` of a loopback client.

    Args:
        redirect_uris: Redirect URIs on ``127.0.0.1`` or ``[::1]``. The authorization server ignores the port.
        scope: Scope the client may request.

    Returns:
        :obj:`str`: ``http://localhost`` with the metadata encoded in the query.
    """
    params: t.List[t.Tuple[str, str]] = []

    for redirect_uri in redirect_uris or ():
        if not is_loopback_redirect_uri(redirect_uri):
            raise ValueError(
                f'Redirect URI of a loopback client must be an http URL on 127.0.0.1 or [::1]: {redirect_uri!r}'
            )

    declared = [get_redirect_uri_without_port(uri) for uri in redirect_uris or ()]
    if declared and sorted(set(declared)) != sorted(DEFAULT_LOOPBACK_REDIRECT_URIS):
        params.extend(('redirect_uri', uri) for uri in dict.fromkeys(declared))

    if scope is not None and scope != ATPROTO_SCOPE:
        _ensure_scope(scope)
        params.append(('scope', scope))

    if not params:
        return LOOPBACK_CLIENT_ID_ORIGIN

    return f'{LOOPBACK_CLIENT_ID_ORIGIN}?{urlencode(params)}'


def _ensure_scope(scope: t.Any) -> None:
    if not isinstance(scope, str) or not _SCOPE.fullmatch(scope):
        raise ValueError('Scope must be a list of scope values separated by single spaces')

    if ATPROTO_SCOPE not in scope.split(' '):
        raise ValueError(f'Scope must include "{ATPROTO_SCOPE}"')


def _ensure_loopback_client_id(client_id: str) -> None:
    rest = client_id[len(LOOPBACK_CLIENT_ID_ORIGIN) :]
    if '#' in rest or (rest and not rest.startswith(('?', '/?')) and rest != '/'):
        raise ValueError('Loopback client ID must be "http://localhost" with an optional query')

    scopes: t.List[str] = []
    for name, value in _parse_query(client_id):
        if name == 'redirect_uri':
            if not is_loopback_redirect_uri(value):
                raise ValueError(f'Invalid redirect URI in loopback client ID: {value!r}')
        elif name == 'scope':
            scopes.append(value)
        else:
            raise ValueError(f'Unexpected parameter in loopback client ID: {name!r}')

    if len(scopes) > 1:
        raise ValueError('Loopback client ID must not declare the scope twice')

    if scopes:
        _ensure_scope(scopes[0])


def _ensure_hosted_client_id(client_id: str) -> None:
    if not client_id.startswith('https://'):
        raise ValueError('Client ID must be an https URL')

    try:
        parts = urlsplit(client_id)
        port = parts.port
    except ValueError as e:
        raise ValueError(f'Client ID is not a URL: {client_id!r}') from e

    if port is not None or '@' in parts.netloc:
        raise ValueError('Client ID must not contain a port or credentials')

    if '#' in client_id:
        raise ValueError('Client ID must not contain a fragment')

    if _is_ip(parts.netloc.strip('[]')):
        raise ValueError('Client ID hostname must not be an IP address')

    if not _is_public_domain(parts.netloc):
        raise ValueError('Client ID hostname must be a lowercase domain name')

    if parts.path in {'', '/'} or parts.path.endswith('/'):
        raise ValueError('Client ID must have a path that does not end with a slash')

    # the authorization server compares the client ID with its parsed form, so it has to be written canonically
    canonical = _CANONICAL_PATH.fullmatch(parts.path) and not _DOT_SEGMENT.search(parts.path)
    if not canonical or not _CANONICAL_QUERY.fullmatch(parts.query):
        raise ValueError('Client ID must be a URL in its canonical form')


def is_loopback_client_id(client_id: str) -> bool:
    return client_id.startswith('http:')


def _validate_common_client_metadata(result: ClientMetadata) -> None:
    redirect_uris = result.get('redirect_uris')
    if not isinstance(redirect_uris, list) or not _string_list(result, 'redirect_uris'):
        raise ValueError('"redirect_uris" must list at least one redirect URI')

    _ensure_scope(result.get('scope'))

    if 'code' not in result.get('response_types', ()):
        raise ValueError('"response_types" must include "code"')

    if 'authorization_code' not in result.get('grant_types', ()):
        raise ValueError('"grant_types" must include "authorization_code"')

    if result.get('dpop_bound_access_tokens') is not True:
        raise ValueError('"dpop_bound_access_tokens" must be true')


def _validate_confidential_client_metadata(result: ClientMetadata, keyset: Keyset) -> None:
    client_id: str = result['client_id']
    if is_loopback_client_id(client_id):
        raise ValueError('A loopback client can not be confidential')

    if result.get('token_endpoint_auth_signing_alg') != CLIENT_ASSERTION_ALG:
        raise ValueError(f'"token_endpoint_auth_signing_alg" must be "{CLIENT_ASSERTION_ALG}"')

    if not len(keyset):
        raise ValueError('A confidential client requires at least one client authentication key')

    if result.get('jwks') and result.get('jwks_uri'):
        raise ValueError('"jwks" and "jwks_uri" are mutually exclusive')

    if not result.get('jwks') and not result.get('jwks_uri'):
        result['jwks'] = keyset.public_jwks

    jwks = result.get('jwks')
    if jwks:
        published = {key.get('kid') for key in jwks.get('keys', ()) if isinstance(key, dict)}
        missing = [key['kid'] for key in keyset.public_jwks['keys'] if key['kid'] not in published]
        if missing:
            raise ValueError(f'Client authentication keys missing from "jwks": {", ".join(missing)}')


def validate_client_metadata(metadata: t.Mapping[str, t.Any], keyset: t.Optional[Keyset] = None) -> ClientMetadata:
    """Validate client metadata against the AT Protocol OAuth profile.

    Args:
        metadata: Client metadata document.
        keyset: Client authentication keys. Published as ``jwks`` when the metadata has neither
            ``jwks`` nor ``jwks_uri``.

    Returns:
        :obj:`dict`: The metadata to publish.

    Raises:
        :class:`ValueError`: The metadata can not be used.
    """
    result: ClientMetadata = dict(metadata)
    keyset = keyset or Keyset()

    client_id = result.get('client_id')
    if not isinstance(client_id, str):
        raise ValueError('"client_id" is required')  # noqa: TRY004

    if is_loopback_client_id(client_id):
        if not client_id.startswith(LOOPBACK_CLIENT_ID_ORIGIN):
            raise ValueError('Client ID must be an https URL')

        _ensure_loopback_client_id(client_id)
    else:
        _ensure_hosted_client_id(client_id)

    _validate_common_client_metadata(result)

    method = result.get('token_endpoint_auth_method')
    if method not in _SUPPORTED_AUTH_METHODS:
        raise ValueError('"token_endpoint_auth_method" must be "none" or "private_key_jwt"')

    if method == AUTH_METHOD_NONE:
        if result.get('token_endpoint_auth_signing_alg'):
            raise ValueError('"token_endpoint_auth_signing_alg" must not be set for the "none" method')

        return result

    _validate_confidential_client_metadata(result, keyset)
    return result


def build_client_metadata(
    client_id: str,
    redirect_uris: t.Sequence[str],
    scope: str,
    keyset: t.Optional[Keyset] = None,
    **extra: t.Any,
) -> ClientMetadata:
    """Build client metadata of a public client, or of a confidential one when keys are given."""
    metadata: ClientMetadata = {
        'client_id': client_id,
        'application_type': 'native' if is_loopback_client_id(client_id) else 'web',
        'grant_types': ['authorization_code', 'refresh_token'],
        'response_types': ['code'],
        'redirect_uris': list(redirect_uris),
        'scope': scope,
        'dpop_bound_access_tokens': True,
        'token_endpoint_auth_method': AUTH_METHOD_NONE,
    }
    if keyset is not None and len(keyset):
        metadata['token_endpoint_auth_method'] = AUTH_METHOD_PRIVATE_KEY_JWT
        metadata['token_endpoint_auth_signing_alg'] = CLIENT_ASSERTION_ALG

    metadata.update(extra)
    return validate_client_metadata(metadata, keyset)
