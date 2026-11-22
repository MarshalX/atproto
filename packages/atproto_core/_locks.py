import threading
import typing as t

LockT = t.TypeVar('LockT')


class KeyedLocks(t.Generic[LockT]):
    """One lock per key, dropped when nobody holds or waits for it."""

    def __init__(self, lock_factory: t.Callable[[], LockT]) -> None:
        self._lock_factory = lock_factory
        self._guard = threading.Lock()
        self._locks: t.Dict[str, t.Tuple[LockT, int]] = {}

    def __len__(self) -> int:
        return len(self._locks)

    def enter(self, key: str) -> LockT:
        with self._guard:
            lock, holders = self._locks.get(key) or (self._lock_factory(), 0)
            self._locks[key] = (lock, holders + 1)

        return lock

    def leave(self, key: str) -> None:
        with self._guard:
            lock, holders = self._locks[key]
            if holders > 1:
                self._locks[key] = (lock, holders - 1)
            else:
                del self._locks[key]
