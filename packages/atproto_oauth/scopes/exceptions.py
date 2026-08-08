"""Scope-specific exceptions."""

from atproto_oauth.exceptions import OAuthError


class ScopeMissingError(OAuthError):
    """Raised when a required scope is missing."""

    def __init__(self, scope: str) -> None:
        self.scope = scope
        super().__init__(f'Missing required scope "{scope}"')
