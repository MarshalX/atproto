import typing as t

import httpx

from atproto_identity.did.resolvers.base_resolver import BaseResolver
from atproto_identity.exceptions import DidWebResolverError, PoorlyFormattedDidError, UnsupportedDidWebPathError

if t.TYPE_CHECKING:
    from atproto_identity.cache.base_cache import DidBaseCache

_DID_DOC_PATH = '/.well-known/did.json'


class DidWebResolver(BaseResolver):
    def __init__(
        self,
        timeout: t.Optional[float] = None,
        cache: t.Optional['DidBaseCache'] = None,
    ) -> None:
        super().__init__(cache)

        self._timeout = timeout

        self._client = httpx.Client()
        self._client_async = httpx.AsyncClient()

    @staticmethod
    def _parse_web_did(did: str) -> str:
        parsed_id = ':'.join(did.split(':')[2:])
        parts = parsed_id.split(':')

        if not parts:
            raise PoorlyFormattedDidError(f'Invalid DID {did}')

        if len(parts) > 1:
            raise UnsupportedDidWebPathError(f'Unsupported DID {did}')

        path = parts[0] + _DID_DOC_PATH
        return f'https://{path}'

    def resolve_without_validation(self, did: str) -> dict:
        url = self._parse_web_did(did)

        try:
            response = self._client.get(url, timeout=self._timeout)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise DidWebResolverError(f'Error resolving DID {did}') from e

    async def resolve_without_validation_async(self, did: str) -> dict:
        url = self._parse_web_did(did)

        try:
            response = await self._client_async.get(url, timeout=self._timeout)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise DidWebResolverError(f'Error resolving DID {did}') from e
