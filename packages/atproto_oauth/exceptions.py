"""OAuth-specific exceptions."""


class OAuthError(Exception):
    """Base exception for OAuth errors."""


class OAuthStateError(OAuthError):
    """OAuth state validation error."""


class OAuthTokenError(OAuthError):
    """OAuth token request error."""


class UnsupportedAuthServerError(OAuthError):
    """Authorization server does not meet ATProto OAuth requirements."""


class DPoPNonceError(OAuthError):
    """DPoP nonce error requiring retry."""
