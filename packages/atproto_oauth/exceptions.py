import typing as t

from atproto_core.exceptions import AtProtocolError


class OAuthError(AtProtocolError):
    """Base exception for OAuth errors."""


class OAuthRequestError(OAuthError):
    """A request to the PDS or the authorization server could not be completed."""


class OAuthResolverError(OAuthError):
    """Identity or server metadata discovery failed."""


class UnsupportedAuthServerError(OAuthResolverError):
    """Server metadata violates the AT Protocol OAuth profile."""


class UnsafeUrlError(OAuthError, ValueError):
    """An outbound URL was rejected by the request policy."""


class OAuthCallbackError(OAuthError):
    """The authorization callback is invalid or reports an error.

    Attributes:
        params: Query parameters of the callback.
        state: Application state passed to ``authorize``, when the flow could be identified.
    """

    def __init__(
        self,
        message: str,
        params: t.Optional[t.Mapping[str, str]] = None,
        state: t.Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.params: t.Dict[str, str] = dict(params or {})
        self.state = state

    @property
    def error(self) -> t.Optional[str]:
        """OAuth error code sent by the authorization server."""
        return self.params.get('error')

    @property
    def error_description(self) -> t.Optional[str]:
        return self.params.get('error_description')


class OAuthResponseError(OAuthError):
    """The authorization server answered with an error.

    Attributes:
        status_code: HTTP status code.
        error: OAuth error code.
        error_description: Human-readable description.
    """

    def __init__(
        self,
        status_code: int,
        error: t.Optional[str] = None,
        error_description: t.Optional[str] = None,
    ) -> None:
        details = error_description or error or 'no details'
        super().__init__(f'Authorization server responded with {status_code}: {details}')
        self.status_code = status_code
        self.error = error
        self.error_description = error_description


class OAuthSessionError(OAuthError):
    """The session of an account is gone or unusable.

    Attributes:
        did: DID of the account.
    """

    def __init__(self, did: str, message: str) -> None:
        super().__init__(f'{message} ({did})')
        self.did = did


class TokenRefreshError(OAuthSessionError):
    """Tokens could not be refreshed."""


class TokenRevokedError(OAuthSessionError):
    """The session was revoked."""

    def __init__(self, did: str, message: str = 'The session was revoked') -> None:
        super().__init__(did, message)


class TokenInvalidError(OAuthSessionError):
    """The resource server keeps rejecting freshly issued tokens."""

    def __init__(self, did: str, message: str = 'The session is no longer accepted by the resource server') -> None:
        super().__init__(did, message)


class AuthMethodUnsatisfiableError(OAuthError):
    """The client authentication method of a session can no longer be used."""


class ScopeMissingError(OAuthError):
    """A required scope was not granted.

    Attributes:
        scope: The missing scope.
    """

    def __init__(self, scope: str) -> None:
        super().__init__(f'Missing required scope "{scope}"')
        self.scope = scope
