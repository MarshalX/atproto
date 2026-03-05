"""OAuth-specific exceptions."""

from atproto_core.exceptions import AtProtocolError


class OAuthError(AtProtocolError):
    """Base exception for OAuth errors."""


class OAuthStateError(OAuthError): ...


class OAuthTokenError(OAuthError): ...


class UnsupportedAuthServerError(OAuthError): ...
