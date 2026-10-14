"""In-memory OAuth stores for development."""

import typing as t
from datetime import datetime, timedelta, timezone

from atproto_oauth.models import OAuthSession, OAuthState
from atproto_oauth.stores.base import SessionStore, StateStore


class MemoryStateStore(StateStore):
    """In-memory OAuth state store.

    Warning:
        This store is not suitable for production use in multi-process
        or distributed environments. Use a persistent store instead.
    """

    def __init__(self, state_ttl_seconds: int = 600) -> None:
        """Initialize memory state store.

        Args:
            state_ttl_seconds: Time-to-live for state entries in seconds.
        """
        self._states: t.Dict[str, OAuthState] = {}
        self._state_ttl = timedelta(seconds=state_ttl_seconds)

    async def save_state(self, state: OAuthState) -> None:
        """Save OAuth state."""
        self._cleanup_expired_states()
        self._states[state.state] = state

    async def get_state(self, state_key: str) -> t.Optional[OAuthState]:
        """Retrieve OAuth state by key."""
        self._cleanup_expired_states()
        return self._states.get(state_key)

    async def delete_state(self, state_key: str) -> None:
        """Delete OAuth state by key."""
        self._states.pop(state_key, None)

    def _cleanup_expired_states(self) -> None:
        """Remove expired state entries."""
        now = datetime.now(timezone.utc)
        expired = [state_key for state_key, state in self._states.items() if (now - state.created_at) > self._state_ttl]
        for state_key in expired:
            del self._states[state_key]


class MemorySessionStore(SessionStore):
    """In-memory OAuth session store.

    Warning:
        This store is not suitable for production use in multi-process
        or distributed environments. Use a persistent store instead.
    """

    def __init__(self) -> None:
        """Initialize memory session store."""
        self._sessions: t.Dict[str, OAuthSession] = {}

    async def save_session(self, session: OAuthSession) -> None:
        """Save OAuth session."""
        self._sessions[session.did] = session

    async def get_session(self, did: str) -> t.Optional[OAuthSession]:
        """Retrieve OAuth session by DID."""
        return self._sessions.get(did)

    async def delete_session(self, did: str) -> None:
        """Delete OAuth session by DID."""
        self._sessions.pop(did, None)
