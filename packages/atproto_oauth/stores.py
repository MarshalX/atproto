import json
import os
import tempfile
import threading
import time
import typing as t

import typing_extensions as te

from atproto_oauth.models import OAuthSessionData, OAuthStateData

V = t.TypeVar('V')


class Store(te.Protocol[V]):
    """Key-value storage."""

    def get(self, key: str) -> t.Optional[V]:
        """Return the value of the key, or :obj:`None` when there is none."""
        ...

    def set(self, key: str, value: V) -> None: ...

    def delete(self, key: str) -> None:
        """Delete the key. Must not fail when there is none."""
        ...


class AsyncStore(te.Protocol[V]):
    """Asynchronous key-value storage."""

    async def get(self, key: str) -> t.Optional[V]:
        """Return the value of the key, or :obj:`None` when there is none."""
        ...

    async def set(self, key: str, value: V) -> None: ...

    async def delete(self, key: str) -> None:
        """Delete the key. Must not fail when there is none."""
        ...


StateStore = Store[OAuthStateData]
SessionStore = Store[OAuthSessionData]
AsyncStateStore = AsyncStore[OAuthStateData]
AsyncSessionStore = AsyncStore[OAuthSessionData]


class MemoryStore(t.Generic[V]):
    """In-memory storage. Thread-safe.

    Warning:
        The content is lost on restart and is not shared between processes.

    Args:
        ttl: Seconds a value is kept for.
        max_size: Number of values to keep. The oldest are dropped first.
    """

    def __init__(self, ttl: t.Optional[float] = None, max_size: t.Optional[int] = None) -> None:
        self._ttl = ttl
        self._max_size = max_size
        self._lock = threading.Lock()
        self._values: t.Dict[str, t.Tuple[float, V]] = {}

    def get(self, key: str) -> t.Optional[V]:
        with self._lock:
            item = self._values.get(key)
            if item is None:
                return None

            stored_at, value = item
            if self._ttl is not None and time.monotonic() - stored_at > self._ttl:
                del self._values[key]
                return None

            return value

    def set(self, key: str, value: V) -> None:
        with self._lock:
            now = time.monotonic()
            self._values.pop(key, None)
            self._values[key] = (now, value)

            # values are ordered by the time they were set, so the expired and the oldest ones come first
            for oldest_key, (stored_at, _) in list(self._values.items()):
                expired = self._ttl is not None and now - stored_at > self._ttl
                over_size = self._max_size is not None and len(self._values) > self._max_size
                if not expired and not over_size:
                    break

                del self._values[oldest_key]

    def delete(self, key: str) -> None:
        with self._lock:
            self._values.pop(key, None)


class JsonFileStore:
    """Storage in one JSON file. For command line tools and scripts used by a single account holder.

    Values are written as returned by their ``to_dict()`` and read back as dictionaries,
    which the OAuth clients accept.

    Warning:
        Sessions hold tokens and private keys. The file is created readable by its owner only;
        keep it out of version control. Concurrent processes are not coordinated.

    Args:
        path: Path of the file. Created on the first write.
    """

    def __init__(self, path: t.Union[str, 'os.PathLike[str]']) -> None:
        self._path = os.fspath(path)
        self._lock = threading.Lock()

    def _read(self) -> t.Dict[str, t.Any]:
        try:
            with open(self._path, encoding='UTF-8') as f:
                content: t.Any = json.load(f)
        except FileNotFoundError:
            return {}

        if not isinstance(content, dict):
            raise ValueError(f'{self._path!r} is not a JSON object')  # noqa: TRY004

        return t.cast('t.Dict[str, t.Any]', content)

    def _write(self, content: t.Dict[str, t.Any]) -> None:
        directory = os.path.dirname(os.path.abspath(self._path))
        # mkstemp creates the file with owner-only permissions
        descriptor, temporary_path = tempfile.mkstemp(dir=directory, prefix='.oauth-', suffix='.tmp')
        try:
            with os.fdopen(descriptor, 'w', encoding='UTF-8') as f:
                json.dump(content, f)

            os.replace(temporary_path, self._path)
        except BaseException:
            if os.path.exists(temporary_path):
                os.unlink(temporary_path)

            raise

    def get(self, key: str) -> t.Optional[t.Dict[str, t.Any]]:
        with self._lock:
            value = self._read().get(key)

        return value if isinstance(value, dict) else None

    def set(self, key: str, value: t.Any) -> None:
        data = value.to_dict() if hasattr(value, 'to_dict') else value
        with self._lock:
            content = self._read()
            content[key] = data
            self._write(content)

    def delete(self, key: str) -> None:
        with self._lock:
            content = self._read()
            if key in content:
                del content[key]
                self._write(content)
