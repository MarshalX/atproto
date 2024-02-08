import typing as t
from dataclasses import dataclass
from enum import Enum

import typing_extensions as te

if t.TYPE_CHECKING:
    from atproto_client import models


class SessionChangeEvent(Enum):
    IMPORT = 'import'
    CREATE = 'creat'
    REFRESH = 'refresh'


_SESSION_STRING_SEPARATOR: te.Final[te.Literal[':::']] = ':::'


@dataclass
class SessionString:
    handle: str
    did: str
    access_jwt: str
    refresh_jwt: str

    def encode(self) -> str:
        payload = [
            self.handle,
            self.did,
            self.access_jwt,
            self.refresh_jwt,
        ]
        return _SESSION_STRING_SEPARATOR.join(payload)

    @classmethod
    def decode(cls, session_string: str) -> 'SessionString':
        handle, did, access_jwt, refresh_jwt = session_string.split(_SESSION_STRING_SEPARATOR)
        return cls(handle, did, access_jwt, refresh_jwt)

    def copy(self) -> 'SessionString':
        return SessionString(self.handle, self.did, self.access_jwt, self.refresh_jwt)


SessionResponse: te.TypeAlias = t.Union[
    'models.ComAtprotoServerCreateSession.Response',
    'models.ComAtprotoServerRefreshSession.Response',
    'SessionString',
]

SessionChangeCallback = t.Callable[[SessionChangeEvent, SessionString], None]
AsyncSessionChangeCallback = t.Callable[[SessionChangeEvent, SessionString], t.Coroutine[t.Any, t.Any, None]]
