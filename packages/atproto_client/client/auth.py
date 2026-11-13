import typing as t

import typing_extensions as te

if t.TYPE_CHECKING:
    import httpx


@te.runtime_checkable
class AuthSession(te.Protocol):
    """Session that authenticates the requests of a client by itself.

    OAuth sessions of :py:mod:`atproto_oauth` implement it.
    """

    @property
    def did(self) -> str:
        """DID of the account."""
        ...

    @property
    def pds_endpoint(self) -> str:
        """URL of the account's PDS."""
        ...

    @property
    def httpx_auth(self) -> 'httpx.Auth':
        """Authentication to send the requests with."""
        ...
