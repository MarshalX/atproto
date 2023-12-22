import typing as t

import httpx

from atproto_identity.did.resolvers.base_resolver import BaseResolver
from atproto_identity.exceptions import DidPlcResolverError

if t.TYPE_CHECKING:
    from atproto_identity.cache.base_cache import DidBaseCache


class DidPlcResolver(BaseResolver):
    def __init__(
        self,
        plc_url: t.Optional[str] = None,
        timeout: t.Optional[float] = None,
        cache: t.Optional['DidBaseCache'] = None,
    ) -> None:
        super().__init__(cache)

        self._plc_url = plc_url
        self._timeout = timeout

        self._client = httpx.Client()
        self._client_async = httpx.AsyncClient()

    def resolve_without_validation(self, did: str) -> t.Optional[dict]:
        try:
            response = self._client.get(f'{self._plc_url}/{did}', timeout=self._timeout)

            if response.status_code == 404:
                return None

            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise DidPlcResolverError(f'Error resolving DID {did}') from e

    async def resolve_without_validation_async(self, did: str) -> t.Optional[dict]:
        try:
            response = await self._client_async.get(f'{self._plc_url}/{did}', timeout=self._timeout)

            if response.status_code == 404:
                return None

            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise DidPlcResolverError(f'Error resolving DID {did}') from e
