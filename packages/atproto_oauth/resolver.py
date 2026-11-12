import re
import typing as t
from dataclasses import dataclass

from atproto_core.exceptions import AtProtocolError

from atproto_oauth._effects import Flow, call, run_flow, run_flow_async
from atproto_oauth.exceptions import OAuthError, OAuthResolverError
from atproto_oauth.metadata import AuthServerMetadata, get_issuer_from_protected_resource_metadata
from atproto_oauth.security import AsyncHttpClient, HttpClient, HttpResponse, ensure_safe_url, get_origin
from atproto_oauth.stores import MemoryStore

if t.TYPE_CHECKING:
    from atproto_identity.resolver import AsyncIdResolver, IdResolver

_CACHE_TTL: t.Final = 60.0
_CACHE_MAX_SIZE: t.Final = 100

_PROTECTED_RESOURCE_PATH: t.Final = '/.well-known/oauth-protected-resource'
_AUTH_SERVER_PATH: t.Final = '/.well-known/oauth-authorization-server'
_HEADERS: t.Final = {'Accept': 'application/json'}

_DID_PLC: t.Final = re.compile(r'did:plc:[a-z2-7]{24}')
_DID_WEB_PREFIX: t.Final = 'did:web:'
_HOSTNAME: t.Final = re.compile(r'[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?(\.[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?)+')
# did:web of a development server: a host without dots, or a port
_DEVELOPMENT_HOSTNAME: t.Final = re.compile(r'[a-z0-9.-]+(%3A[0-9]{1,5})?', re.IGNORECASE)


@dataclass(frozen=True)
class ResolvedIdentity:
    """Account an authorization flow is started for.

    Attributes:
        did: DID of the account.
        pds: URL of the account's PDS.
        handle: Handle of the account, when the DID document and the handle point at each other.
    """

    did: str
    pds: str
    handle: t.Optional[str] = None


@dataclass(frozen=True)
class ResolvedServer:
    """Authorization server to send a user to.

    Attributes:
        server: Metadata of the authorization server.
        identity: Account the server is authoritative for. :obj:`None` when resolved from a server URL.
    """

    server: AuthServerMetadata
    identity: t.Optional[ResolvedIdentity] = None


def is_service_url(identifier: str) -> bool:
    return identifier.startswith(('https://', 'http://'))


def is_atproto_did(value: str) -> bool:
    if _DID_PLC.fullmatch(value):
        return True

    return value.startswith(_DID_WEB_PREFIX) and bool(_DEVELOPMENT_HOSTNAME.fullmatch(value[len(_DID_WEB_PREFIX) :]))


def _normalize_handle(handle: str) -> str:
    return handle.lstrip('@').lower()


def ensure_safe_identifier(identifier: str, allow_http: bool) -> None:
    """Ensure that resolving a handle or a DID only requests URLs the request policy allows.

    The identity resolver requests ``https://<handle>/`` and, for ``did:web``, ``https://<host>/``,
    so an identifier that is not a plain hostname would let its author choose the URL.

    Raises:
        :class:`atproto_oauth.exceptions.OAuthResolverError`: The identifier is not a handle or a supported DID.
        :class:`atproto_oauth.exceptions.UnsafeUrlError`: The identifier points at a host that must not be requested.
    """
    if _DID_PLC.fullmatch(identifier):
        return

    if identifier.startswith('did:'):
        host = identifier[len(_DID_WEB_PREFIX) :] if identifier.startswith(_DID_WEB_PREFIX) else ''
        pattern = _DEVELOPMENT_HOSTNAME if allow_http else _HOSTNAME
        if not pattern.fullmatch(host):
            raise OAuthResolverError(f'Not a supported DID: {identifier!r}')

        ensure_safe_url(f'https://{host.replace("%3A", ":").replace("%3a", ":")}', allow_http)
        return

    handle = _normalize_handle(identifier)
    if not _HOSTNAME.fullmatch(handle):
        raise OAuthResolverError(f'Not a handle or a DID: {identifier!r}')

    ensure_safe_url(f'https://{handle}', allow_http)


def _get_identity(identifier: str, did: str, handle: t.Optional[str], pds: t.Optional[str]) -> ResolvedIdentity:
    if not pds:
        raise OAuthResolverError(f'DID document of {did!r} does not declare a PDS')

    is_handle = not identifier.startswith('did:')
    verified_handle = handle.lower() if handle else None

    if is_handle and verified_handle != _normalize_handle(identifier):
        raise OAuthResolverError(f'DID document of {did!r} does not include the handle {identifier!r}')

    return ResolvedIdentity(did=did, pds=pds, handle=verified_handle if is_handle else None)


def _get_origin(url: str) -> str:
    try:
        return get_origin(url)
    except ValueError as e:
        raise OAuthResolverError(f'Not a URL: {url!r}') from e


def _decode_metadata(response: HttpResponse, url: str) -> t.Any:
    if response.status_code != 200:
        raise OAuthResolverError(f'Unexpected status code {response.status_code} for {url!r}')

    if not response.is_json:
        raise OAuthResolverError(f'Unexpected content type for {url!r}')

    return response.json()


class _OAuthResolverBase:
    def __init__(self, id_resolver: t.Any, http: t.Union[HttpClient, AsyncHttpClient], allow_http: bool) -> None:
        self._id_resolver = id_resolver
        self._http = http
        self._allow_http = allow_http
        self._issuers: MemoryStore[str] = MemoryStore(ttl=_CACHE_TTL, max_size=_CACHE_MAX_SIZE)
        self._servers: MemoryStore[AuthServerMetadata] = MemoryStore(ttl=_CACHE_TTL, max_size=_CACHE_MAX_SIZE)

    def _resolve_flow(self, identifier: str) -> Flow[ResolvedServer]:
        if is_service_url(identifier):
            return (yield from self._resolve_from_service_flow(identifier))

        return (yield from self._resolve_from_identity_flow(identifier, False))

    def _resolve_from_identity_flow(self, identifier: str, no_cache: bool) -> Flow[ResolvedServer]:
        identity = yield from self._resolve_identity_flow(identifier, no_cache)
        server = yield from self._get_resource_server_metadata_flow(identity.pds, no_cache)

        return ResolvedServer(server, identity)

    def _resolve_from_service_flow(self, url: str) -> Flow[ResolvedServer]:
        try:
            return ResolvedServer((yield from self._get_resource_server_metadata_flow(url, False)))
        except OAuthResolverError:
            try:
                return ResolvedServer((yield from self._get_auth_server_metadata_flow(url.rstrip('/'), False)))
            except OAuthError:
                pass

            raise

    def _resolve_identity_flow(self, identifier: str, no_cache: bool) -> Flow[ResolvedIdentity]:
        ensure_safe_identifier(identifier, self._allow_http)

        try:
            did = identifier
            if not identifier.startswith('did:'):
                handle = _normalize_handle(identifier)
                resolved: t.Optional[str] = yield call(self._id_resolver.handle.resolve, handle)
                if not resolved:
                    raise OAuthResolverError(f'Handle {identifier!r} does not resolve to a DID')

                did = resolved
                ensure_safe_identifier(did, self._allow_http)

            data = yield call(self._id_resolver.did.resolve_atproto_data, did, no_cache)
        except OAuthError:
            raise
        except AtProtocolError as e:
            raise OAuthResolverError(f'Failed to resolve identity {identifier!r}: {e}') from e

        return _get_identity(identifier, did, data.handle, data.pds)

    def _get_resource_server_metadata_flow(self, pds_url: str, no_cache: bool) -> Flow[AuthServerMetadata]:
        origin = _get_origin(pds_url)

        issuer = None if no_cache else self._issuers.get(origin)
        if issuer is None:
            url = f'{origin}{_PROTECTED_RESOURCE_PATH}'
            response: HttpResponse = yield call(self._http.request, 'GET', url, headers=_HEADERS)
            issuer = get_issuer_from_protected_resource_metadata(
                _decode_metadata(response, url), origin, self._allow_http
            )
            self._issuers.set(origin, issuer)

        server = yield from self._get_auth_server_metadata_flow(issuer, no_cache)
        if server.protected_resources is not None and origin not in server.protected_resources:
            raise OAuthResolverError(f'PDS {origin!r} is not protected by issuer {server.issuer!r}')

        return server

    def _get_auth_server_metadata_flow(self, issuer: str, no_cache: bool) -> Flow[AuthServerMetadata]:
        server = None if no_cache else self._servers.get(issuer)
        if server is None:
            url = f'{issuer}{_AUTH_SERVER_PATH}'
            response: HttpResponse = yield call(self._http.request, 'GET', url, headers=_HEADERS)
            server = AuthServerMetadata.from_dict(_decode_metadata(response, url), issuer, self._allow_http)
            self._servers.set(issuer, server)

        return server


class OAuthResolver(_OAuthResolverBase):
    """Find the authorization server of an account or of a PDS.

    Args:
        id_resolver: Identity resolver.
        http: Client for requests to the PDS and the authorization server.
        allow_http: Accept ``http`` URLs. For development environments.
    """

    def __init__(self, id_resolver: 'IdResolver', http: HttpClient, allow_http: bool = False) -> None:
        super().__init__(id_resolver, http, allow_http)

    def resolve(self, identifier: str) -> ResolvedServer:
        """Resolve the authorization server of a handle, a DID, a PDS URL or an entryway URL.

        Raises:
            :class:`atproto_oauth.exceptions.OAuthResolverError`: The identifier can not be resolved.
        """
        return run_flow(self._resolve_flow(identifier))

    def resolve_from_identity(self, identifier: str, no_cache: bool = False) -> ResolvedServer:
        """Resolve the authorization server of a handle or a DID.

        Args:
            identifier: Handle or DID.
            no_cache: Bypass every cache.
        """
        return run_flow(self._resolve_from_identity_flow(identifier, no_cache))

    def resolve_from_service(self, url: str) -> ResolvedServer:
        """Resolve the authorization server from the URL of a PDS, falling back to treating it as an issuer."""
        return run_flow(self._resolve_from_service_flow(url))

    def resolve_identity(self, identifier: str, no_cache: bool = False) -> ResolvedIdentity:
        """Resolve a handle or a DID to the account it identifies.

        Args:
            identifier: Handle or DID.
            no_cache: Bypass the cache of the identity resolver.
        """
        return run_flow(self._resolve_identity_flow(identifier, no_cache))

    def get_resource_server_metadata(self, pds_url: str, no_cache: bool = False) -> AuthServerMetadata:
        """Return the metadata of the authorization server that protects a PDS."""
        return run_flow(self._get_resource_server_metadata_flow(pds_url, no_cache))

    def get_auth_server_metadata(self, issuer: str, no_cache: bool = False) -> AuthServerMetadata:
        """Return the validated metadata of an authorization server."""
        return run_flow(self._get_auth_server_metadata_flow(issuer, no_cache))


class AsyncOAuthResolver(_OAuthResolverBase):
    """Find the authorization server of an account or of a PDS.

    Args:
        id_resolver: Identity resolver.
        http: Client for requests to the PDS and the authorization server.
        allow_http: Accept ``http`` URLs. For development environments.
    """

    def __init__(self, id_resolver: 'AsyncIdResolver', http: AsyncHttpClient, allow_http: bool = False) -> None:
        super().__init__(id_resolver, http, allow_http)

    async def resolve(self, identifier: str) -> ResolvedServer:
        """Resolve the authorization server of a handle, a DID, a PDS URL or an entryway URL.

        Raises:
            :class:`atproto_oauth.exceptions.OAuthResolverError`: The identifier can not be resolved.
        """
        return await run_flow_async(self._resolve_flow(identifier))

    async def resolve_from_identity(self, identifier: str, no_cache: bool = False) -> ResolvedServer:
        """Resolve the authorization server of a handle or a DID.

        Args:
            identifier: Handle or DID.
            no_cache: Bypass every cache.
        """
        return await run_flow_async(self._resolve_from_identity_flow(identifier, no_cache))

    async def resolve_from_service(self, url: str) -> ResolvedServer:
        """Resolve the authorization server from the URL of a PDS, falling back to treating it as an issuer."""
        return await run_flow_async(self._resolve_from_service_flow(url))

    async def resolve_identity(self, identifier: str, no_cache: bool = False) -> ResolvedIdentity:
        """Resolve a handle or a DID to the account it identifies.

        Args:
            identifier: Handle or DID.
            no_cache: Bypass the cache of the identity resolver.
        """
        return await run_flow_async(self._resolve_identity_flow(identifier, no_cache))

    async def get_resource_server_metadata(self, pds_url: str, no_cache: bool = False) -> AuthServerMetadata:
        """Return the metadata of the authorization server that protects a PDS."""
        return await run_flow_async(self._get_resource_server_metadata_flow(pds_url, no_cache))

    async def get_auth_server_metadata(self, issuer: str, no_cache: bool = False) -> AuthServerMetadata:
        """Return the validated metadata of an authorization server."""
        return await run_flow_async(self._get_auth_server_metadata_flow(issuer, no_cache))
