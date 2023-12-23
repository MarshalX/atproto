import typing as t
from abc import ABC, abstractmethod

from atproto_core.did_doc import is_valid_did_doc, parse_did_doc

from atproto_identity.did.atproto_data import ensure_atproto_document, ensure_atproto_key
from atproto_identity.exceptions import DidNotFoundError, PoorlyFormattedDidDocumentError

if t.TYPE_CHECKING:
    from atproto_core.did_doc import DidDocument

    from atproto_identity.cache.base_cache import AsyncDidBaseCache, DidBaseCache
    from atproto_identity.did.models import AtprotoData

_DID_KEY_PREFIX = 'did:key:'


class _BaseResolver:
    @staticmethod
    def validate_did_doc(did: str, value: dict) -> 'DidDocument':
        # it performs double parsing, but it's ok for now
        if not is_valid_did_doc(value):
            raise PoorlyFormattedDidDocumentError(f'Invalid DID document for DID {did}')

        did_doc = parse_did_doc(value)
        if did_doc.id != did:
            raise PoorlyFormattedDidDocumentError(f'Invalid DID document for DID {did}')

        return did_doc


class BaseResolver(_BaseResolver, ABC):
    def __init__(self, cache: 'DidBaseCache' = None) -> None:
        self._cache = cache

    @abstractmethod
    def resolve_without_validation(self, did: str) -> t.Optional[dict]:
        raise NotImplementedError

    def resolve_no_cache(self, did: str) -> t.Optional['DidDocument']:
        """Resolve DID without cache.

        Args:
            did: DID.

        Returns:
            :obj:`DidDocument`: DID document or ``None`` if not found.
        """
        value = self.resolve_without_validation(did)
        if value is None:
            return None

        return self.validate_did_doc(did, value)

    def refresh_cache(self, did: str) -> None:
        """Refresh cached DID.

        Args:
            did: DID.
        """
        if self._cache is None:
            return

        self._cache.refresh(did, lambda: self.resolve_no_cache(did))

    def resolve(self, did: str, force_refresh: bool = False) -> t.Optional['DidDocument']:
        """Resolve DID.

        Args:
            did: DID.
            force_refresh: Force refresh cache.

        Returns:
            :obj:`DidDocument`: DID document or ``None`` if not found.
        """
        if self._cache and not force_refresh:
            cached_result = self._cache.get(did)
            if cached_result is not None and not cached_result.expired:
                if cached_result.stale:
                    self.refresh_cache(did)
                    cached_result = self._cache.get(did)

                return cached_result.document

        did_doc = self.resolve_no_cache(did)
        if did_doc is None:
            if self._cache:
                self._cache.delete(did)

            return None

        if self._cache:
            self._cache.set(did, did_doc)

        return did_doc

    def ensure_resolve(self, did: str, force_refresh: bool = False) -> 'DidDocument':
        """Ensure DID is resolved.

        Args:
            did: DID.
            force_refresh: Force refresh cache.

        Returns:
            :obj:`DidDocument`: DID document.

        Raises:
            :obj:`DidNotFoundError`: DID not found.
        """
        did_doc = self.resolve(did, force_refresh)
        if did_doc is None:
            raise DidNotFoundError(f'Unable to resolve DID {did}')

        return did_doc

    def resolve_atproto_data(self, did: str, force_refresh: bool = False) -> 'AtprotoData':
        """Not implemented yet."""
        did_doc = self.ensure_resolve(did, force_refresh)
        return ensure_atproto_document(did_doc)

    def resolve_atproto_key(self, did: str, force_refresh: bool = False) -> str:
        """Not implemented yet."""
        if did.startswith(_DID_KEY_PREFIX):
            return did

        did_doc = self.ensure_resolve(did, force_refresh)
        return ensure_atproto_key(did_doc)


class AsyncBaseResolver(_BaseResolver, ABC):
    def __init__(self, cache: 'AsyncDidBaseCache' = None) -> None:
        self._cache = cache

    @abstractmethod
    async def resolve_without_validation(self, did: str) -> t.Optional[dict]:
        raise NotImplementedError

    async def resolve_no_cache(self, did: str) -> t.Optional['DidDocument']:
        """Resolve DID without cache.

        Args:
            did: DID.

        Returns:
            :obj:`DidDocument`: DID document or ``None`` if not found.
        """
        value = await self.resolve_without_validation(did)
        if value is None:
            return None

        return self.validate_did_doc(did, value)

    async def refresh_cache(self, did: str) -> None:
        """Refresh cached DID.

        Args:
            did: DID.
        """
        if self._cache is None:
            return

        await self._cache.refresh(did, lambda: self.resolve_no_cache(did))

    async def resolve(self, did: str, force_refresh: bool = False) -> t.Optional['DidDocument']:
        """Resolve DID.

        Args:
            did: DID.
            force_refresh: Force refresh cache.

        Returns:
            :obj:`DidDocument`: DID document or ``None`` if not found.
        """
        if self._cache and not force_refresh:
            cached_result = await self._cache.get(did)
            if cached_result is not None and not cached_result.expired:
                if cached_result.stale:
                    await self.refresh_cache(did)
                    cached_result = await self._cache.get(did)

                return cached_result.document

        did_doc = await self.resolve_no_cache(did)
        if did_doc is None:
            if self._cache:
                await self._cache.delete(did)

            return None

        if self._cache:
            await self._cache.set(did, did_doc)

        return did_doc

    async def ensure_resolve(self, did: str, force_refresh: bool = False) -> 'DidDocument':
        """Ensure DID is resolved.

        Args:
            did: DID.
            force_refresh: Force refresh cache.

        Returns:
            :obj:`DidDocument`: DID document.

        Raises:
            :obj:`DidNotFoundError`: DID not found.
        """
        did_doc = await self.resolve(did, force_refresh)
        if did_doc is None:
            raise DidNotFoundError(f'Unable to resolve DID {did}')

        return did_doc

    async def resolve_atproto_data(self, did: str, force_refresh: bool = False) -> 'AtprotoData':
        """Not implemented yet."""
        did_doc = await self.ensure_resolve(did, force_refresh)
        return ensure_atproto_document(did_doc)

    async def resolve_atproto_key(self, did: str, force_refresh: bool = False) -> str:
        """Not implemented yet."""
        if did.startswith(_DID_KEY_PREFIX):
            return did

        did_doc = await self.ensure_resolve(did, force_refresh)
        return ensure_atproto_key(did_doc)
