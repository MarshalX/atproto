import typing as t
from dataclasses import dataclass
from enum import Enum

import typing_extensions as te
from atproto_core.did_doc import DidDocument, is_valid_did_doc

if t.TYPE_CHECKING:
    from atproto_client import models


class SessionEvent(Enum):
    IMPORT = 'import'
    CREATE = 'creat'
    REFRESH = 'refresh'


_SESSION_STRING_SEPARATOR: t.Final[te.Literal[':::']] = ':::'


@dataclass
class Session:
    handle: str
    did: str
    access_jwt: str
    refresh_jwt: str
    pds_endpoint: t.Optional[str] = 'https://bsky.social'  # Backward compatibility for old sessions

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
            self.pds_endpoint,
        ]
        return _SESSION_STRING_SEPARATOR.join(payload)

    @classmethod
    def decode(cls, session_string: str) -> 'Session':
        fields = session_string.split(_SESSION_STRING_SEPARATOR)

        if len(fields) == 4:
            # Old session format
            handle, did, access_jwt, refresh_jwt = fields
            return cls(handle, did, access_jwt, refresh_jwt)

        handle, did, access_jwt, refresh_jwt, pds_endpoint = session_string.split(_SESSION_STRING_SEPARATOR)
        return cls(handle, did, access_jwt, refresh_jwt, pds_endpoint)

    def copy(self) -> 'Session':
        return Session(self.handle, self.did, self.access_jwt, self.refresh_jwt, self.pds_endpoint)

    #: Alias for :attr:`encode`
    export = encode


SessionResponse: te.TypeAlias = t.Union[
    'models.ComAtprotoServerCreateSession.Response',
    'models.ComAtprotoServerRefreshSession.Response',
    'Session',
]

SessionChangeCallback = t.Callable[[SessionEvent, Session], None]
AsyncSessionChangeCallback = t.Callable[[SessionEvent, Session], t.Coroutine[t.Any, t.Any, None]]


def get_session_pds_endpoint(session: SessionResponse) -> t.Optional[str]:
    """Return the PDS endpoint of the given session.

    Note:
        Return :obj:`None` for self-hosted PDSs.
    """
    if isinstance(session, Session):
        return session.pds_endpoint

    if session.did_doc and is_valid_did_doc(session.did_doc):
        doc = DidDocument.from_dict(session.did_doc)
        return doc.get_pds_endpoint()

    return None
