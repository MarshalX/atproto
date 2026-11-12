import typing as t
from dataclasses import dataclass, field
from datetime import datetime, timezone

from atproto_crypto.jwk import Jwk

AUTH_METHOD_NONE: t.Final = 'none'
AUTH_METHOD_PRIVATE_KEY_JWT: t.Final = 'private_key_jwt'


def _require(data: t.Mapping[str, t.Any], name: str, kind: t.Union[type, t.Tuple[type, ...]]) -> t.Any:
    value = data.get(name)
    if not isinstance(value, kind) or isinstance(value, bool):
        raise ValueError(f'"{name}" is missing or invalid')  # noqa: TRY004

    return value


def _optional(data: t.Mapping[str, t.Any], name: str, kind: t.Union[type, t.Tuple[type, ...]]) -> t.Any:
    if data.get(name) is None:
        return None

    return _require(data, name, kind)


@dataclass(frozen=True)
class AuthMethod:
    """How the client authenticates to the authorization server during a session."""

    method: str
    kid: t.Optional[str] = None

    def to_dict(self) -> t.Dict[str, t.Any]:
        if self.kid is None:
            return {'method': self.method}

        return {'method': self.method, 'kid': self.kid}

    @classmethod
    def from_dict(cls, data: t.Mapping[str, t.Any]) -> 'AuthMethod':
        method = _require(data, 'method', str)
        kid = _optional(data, 'kid', str)
        if method == AUTH_METHOD_NONE and kid is None:
            return cls(method)

        if method == AUTH_METHOD_PRIVATE_KEY_JWT and kid:
            return cls(method, kid)

        raise ValueError('"auth_method" is invalid')


@dataclass(frozen=True)
class TokenSet:
    """Tokens of a session.

    Attributes:
        iss: Issuer of the authorization server.
        sub: DID of the account.
        aud: URL of the account's PDS.
        expires_at: Expiration of the access token as a Unix timestamp.
    """

    iss: str
    sub: str
    aud: str
    scope: str
    access_token: str = field(repr=False)
    token_type: str = 'DPoP'  # noqa: S105
    refresh_token: t.Optional[str] = field(default=None, repr=False)
    expires_at: t.Optional[float] = None

    def to_dict(self) -> t.Dict[str, t.Any]:
        return {
            'iss': self.iss,
            'sub': self.sub,
            'aud': self.aud,
            'scope': self.scope,
            'access_token': self.access_token,
            'token_type': self.token_type,
            'refresh_token': self.refresh_token,
            'expires_at': self.expires_at,
        }

    @classmethod
    def from_dict(cls, data: t.Mapping[str, t.Any]) -> 'TokenSet':
        expires_at = _optional(data, 'expires_at', (int, float))
        return cls(
            iss=_require(data, 'iss', str),
            sub=_require(data, 'sub', str),
            aud=_require(data, 'aud', str),
            scope=_require(data, 'scope', str),
            access_token=_require(data, 'access_token', str),
            token_type=_require(data, 'token_type', str),
            refresh_token=_optional(data, 'refresh_token', str),
            expires_at=None if expires_at is None else float(expires_at),
        )


@dataclass(frozen=True)
class OAuthSessionData:
    """Everything needed to resume a session. Stored by DID.

    Warning:
        Contains the tokens and the private DPoP key of the session.
    """

    dpop_jwk: Jwk = field(repr=False)
    auth_method: AuthMethod
    token_set: TokenSet

    def to_dict(self) -> t.Dict[str, t.Any]:
        """Convert to JSON-serializable data."""
        return {
            'dpop_jwk': dict(self.dpop_jwk),
            'auth_method': self.auth_method.to_dict(),
            'token_set': self.token_set.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: t.Mapping[str, t.Any]) -> 'OAuthSessionData':
        """Restore from :meth:`to_dict`. Unknown keys are ignored.

        Raises:
            :class:`ValueError`: The data is not a session.
        """
        return cls(
            dpop_jwk=dict(_require(data, 'dpop_jwk', dict)),
            auth_method=AuthMethod.from_dict(_require(data, 'auth_method', dict)),
            token_set=TokenSet.from_dict(_require(data, 'token_set', dict)),
        )


@dataclass(frozen=True)
class OAuthStateData:
    """Authorization request in progress. Stored by ``state``.

    Warning:
        Contains the PKCE verifier and the private DPoP key of the session being created.
    """

    iss: str
    dpop_jwk: Jwk = field(repr=False)
    auth_method: AuthMethod
    pkce_verifier: str = field(repr=False)
    redirect_uri: str
    created_at: float
    did: t.Optional[str] = None
    app_state: t.Optional[str] = None

    def to_dict(self) -> t.Dict[str, t.Any]:
        """Convert to JSON-serializable data."""
        return {
            'iss': self.iss,
            'dpop_jwk': dict(self.dpop_jwk),
            'auth_method': self.auth_method.to_dict(),
            'pkce_verifier': self.pkce_verifier,
            'redirect_uri': self.redirect_uri,
            'created_at': self.created_at,
            'did': self.did,
            'app_state': self.app_state,
        }

    @classmethod
    def from_dict(cls, data: t.Mapping[str, t.Any]) -> 'OAuthStateData':
        """Restore from :meth:`to_dict`. Unknown keys are ignored.

        Raises:
            :class:`ValueError`: The data is not an authorization request.
        """
        return cls(
            iss=_require(data, 'iss', str),
            dpop_jwk=dict(_require(data, 'dpop_jwk', dict)),
            auth_method=AuthMethod.from_dict(_require(data, 'auth_method', dict)),
            pkce_verifier=_require(data, 'pkce_verifier', str),
            redirect_uri=_require(data, 'redirect_uri', str),
            created_at=float(_require(data, 'created_at', (int, float))),
            did=_optional(data, 'did', str),
            app_state=_optional(data, 'app_state', str),
        )


@dataclass(frozen=True)
class TokenResponse:
    """Validated token response of the authorization server."""

    access_token: str = field(repr=False)
    token_type: str
    scope: str
    sub: str
    refresh_token: t.Optional[str] = field(default=None, repr=False)
    expires_in: t.Optional[float] = None


@dataclass(frozen=True)
class TokenInfo:
    """Description of the tokens of a session, without the tokens.

    Attributes:
        sub: DID of the account.
        iss: Issuer of the authorization server.
        aud: URL of the account's PDS.
        scope: Granted scope.
        expires_at: Expiration of the access token.
    """

    sub: str
    iss: str
    aud: str
    scope: str
    expires_at: t.Optional[datetime] = field(default=None)

    @property
    def expired(self) -> t.Optional[bool]:
        """Whether the access token expired. :obj:`None` when the expiration is unknown."""
        if self.expires_at is None:
            return None

        return self.expires_at.timestamp() < datetime.now(timezone.utc).timestamp() - 5

    @classmethod
    def from_token_set(cls, token_set: TokenSet) -> 'TokenInfo':
        expires_at = None
        if token_set.expires_at is not None:
            expires_at = datetime.fromtimestamp(token_set.expires_at, timezone.utc)

        return cls(token_set.sub, token_set.iss, token_set.aud, token_set.scope, expires_at)
