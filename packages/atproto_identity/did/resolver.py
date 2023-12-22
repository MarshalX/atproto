import typing as t

from atproto_identity.did.resolvers.base_resolver import BaseResolver
from atproto_identity.did.resolvers.plc_resolver import DidPlcResolver
from atproto_identity.did.resolvers.web_resolver import DidWebResolver
from atproto_identity.exceptions import PoorlyFormattedDidError, UnsupportedDidMethodError

if t.TYPE_CHECKING:
    from atproto_identity.cache.base_cache import DidBaseCache


_BASE_PLC_URL = 'https://plc.directory'
_DEFAULT_TIMEOUT = 3.0
_DID_PREFIX = 'did'


class DidResolver(BaseResolver):
    def __init__(
        self,
        plc_url: t.Optional[str] = None,
        timeout: t.Optional[float] = None,
        cache: t.Optional['DidBaseCache'] = None,
    ) -> None:
        super().__init__(cache)

        if plc_url is None:
            plc_url = _BASE_PLC_URL

        if timeout is None:
            timeout = _DEFAULT_TIMEOUT

        self._methods = {'plc': DidPlcResolver(plc_url, timeout, cache), 'web': DidWebResolver(timeout)}

    def _get_resolver_method(self, did: str) -> BaseResolver:
        parts = did.split(':')
        if not parts:
            raise PoorlyFormattedDidError(f'Invalid DID {did}')

        if parts[0] != _DID_PREFIX:
            raise PoorlyFormattedDidError(f'Invalid DID {did}')

        if len(parts) < 2:
            raise PoorlyFormattedDidError(f'Invalid DID {did}')

        method = parts[1]
        if method not in self._methods:
            raise UnsupportedDidMethodError(f'Invalid DID {did}')

        return self._methods[method]

    def resolve_without_validation(self, did: str) -> t.Optional[dict]:
        return self._get_resolver_method(did).resolve_without_validation(did)

    async def resolve_without_validation_async(self, did: str) -> t.Optional[dict]:
        return await self._get_resolver_method(did).resolve_without_validation_async(did)
