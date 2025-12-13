"""Abstract base classes for OAuth stores."""

import typing as t
from abc import ABC, abstractmethod

if t.TYPE_CHECKING:
    from atproto_oauth.models import OAuthSession, OAuthState


class StateStore(ABC):
    """Abstract store for OAuth state during authorization flow."""

    @abstractmethod
    async def save_state(self, state: 'OAuthState') -> None:
        """Save OAuth state.

        Args:
            state: OAuth state object to save.
        """

    @abstractmethod
    async def get_state(self, state_key: str) -> t.Optional['OAuthState']:
        """Retrieve OAuth state by key.

        Args:
            state_key: State identifier.

        Returns:
            OAuth state object if found, None otherwise.
        """

    @abstractmethod
    async def delete_state(self, state_key: str) -> None:
        """Delete OAuth state by key.

        Args:
            state_key: State identifier.
        """


class SessionStore(ABC):
    """Abstract store for OAuth sessions."""

    @abstractmethod
    async def save_session(self, session: 'OAuthSession') -> None:
        """Save OAuth session.

        Args:
            session: OAuth session object to save.
        """

    @abstractmethod
    async def get_session(self, did: str) -> t.Optional['OAuthSession']:
        """Retrieve OAuth session by DID.

        Args:
            did: User DID.

        Returns:
            OAuth session object if found, None otherwise.
        """

    @abstractmethod
    async def delete_session(self, did: str) -> None:
        """Delete OAuth session by DID.

        Args:
            did: User DID.
        """
