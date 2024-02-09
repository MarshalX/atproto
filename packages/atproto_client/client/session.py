import typing as t
from dataclasses import dataclass
from enum import Enum

import typing_extensions as te

if t.TYPE_CHECKING:
    from atproto_client import models


class SessionEvent(Enum):
    IMPORT = 'import'
    CREATE = 'creat'
    REFRESH = 'refresh'


_SESSION_STRING_SEPARATOR: te.Final[te.Literal[':::']] = ':::'


@dataclass
class Session:
    handle: str
    did: str
    access_jwt: str
    refresh_jwt: str

    def __repr__(self) -> str:
        return f'<Session handle={self.handle} did={self.did}>'

    def __str__(self) -> str:
        return self.encode()

    def encode(self) -> str:
        payload = [
            self.handle,
            self.did,
            self.access_jwt,
            self.refresh_jwt,
        ]
        return _SESSION_STRING_SEPARATOR.join(payload)

    @classmethod
    def decode(cls, session_string: str) -> 'Session':
        handle, did, access_jwt, refresh_jwt = session_string.split(_SESSION_STRING_SEPARATOR)
        return cls(handle, did, access_jwt, refresh_jwt)

    def copy(self) -> 'Session':
        return Session(self.handle, self.did, self.access_jwt, self.refresh_jwt)

    #: Alias for :attr:`encode`
    export = encode


SessionResponse: te.TypeAlias = t.Union[
    'models.ComAtprotoServerCreateSession.Response',
    'models.ComAtprotoServerRefreshSession.Response',
    'Session',
]

SessionChangeCallback = t.Callable[[SessionEvent, Session], None]
AsyncSessionChangeCallback = t.Callable[[SessionEvent, Session], t.Coroutine[t.Any, t.Any, None]]


class SessionString(Session):
    def __init_subclass__(cls, *args, **kwargs: t.Any) -> None:
        import warnings

        warnings.warn('SessionString class is deprecated. Use Session class instead.', DeprecationWarning, stacklevel=2)
        super().__init_subclass__(*args, **kwargs)

    def __init__(self, *args, **kwargs: t.Any) -> None:
        import warnings

        warnings.warn('SessionString class is deprecated. Use Session class instead.', DeprecationWarning, stacklevel=2)
        super().__init__(*args, **kwargs)
