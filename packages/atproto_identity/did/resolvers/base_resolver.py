import typing as t
from abc import ABC, abstractmethod

if t.TYPE_CHECKING:
    from atproto_identity.cache.base_cache import DidBaseCache


class BaseResolver(ABC):
    def __init__(self, cache: 'DidBaseCache' = None) -> None:
        self._cache = cache

    @abstractmethod
    def resolve_without_validation(self, did: str) -> t.Optional[dict]:
        raise NotImplementedError

    @abstractmethod
    async def resolve_without_validation_async(self, did: str) -> t.Optional[dict]:
        raise NotImplementedError
