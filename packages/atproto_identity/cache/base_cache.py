import typing as t
from abc import ABC, abstractmethod

if t.TYPE_CHECKING:
    from atproto_core.did_doc import DidDocument

    from atproto_identity.cache.models import CachedDidResult


_DEFAULT_STALE_TTL = 60 * 60  # 1 hour
_DEFAULT_MAX_TTL = 60 * 60 * 24  # 1 day


GetDocCallback = t.Callable[[], t.Optional['DidDocument']]
AsyncGetDocCallback = t.Callable[[], t.Coroutine[t.Any, t.Any, t.Optional['DidDocument']]]


class DidBaseCache(ABC):
    def __init__(self, stale_ttl: t.Optional[int] = None, max_ttl: t.Optional[int] = None) -> None:
        self.stale_ttl = stale_ttl or _DEFAULT_STALE_TTL
        self.max_ttl = max_ttl or _DEFAULT_MAX_TTL

    @abstractmethod
    def get(self, did: str) -> t.Optional['CachedDidResult']:
        raise NotImplementedError

    @abstractmethod
    def set(self, did: str, document: 'DidDocument') -> None:
        raise NotImplementedError

    @abstractmethod
    def refresh(self, did: str, get_doc_callback: GetDocCallback) -> None:
        raise NotImplementedError

    @abstractmethod
    async def refresh_async(self, did: str, get_doc_callback: AsyncGetDocCallback) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, did: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        raise NotImplementedError
