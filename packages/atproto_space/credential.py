import time
import typing as t

from atproto_crypto.did import private_key_to_did_key

from atproto_space.exceptions import SpaceTokenError
from atproto_space.http_signature import create_credential_headers
from atproto_space.tokens import parse_space_token

if t.TYPE_CHECKING:
    from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey

_RENEWAL_MARGIN: t.Final = 60


class SpaceCredential:
    """Space credential together with the key it is bound to.

    Args:
        token: Space credential.
        private_key: P-256 private key that the credential is bound to.
        renew_at: Unix timestamp after which the credential should be renewed.
        space_rev: Revision of the space when the credential was issued.
    """

    def __init__(
        self,
        token: str,
        private_key: 'EllipticCurvePrivateKey',
        renew_at: float,
        space_rev: t.Optional[str] = None,
    ) -> None:
        self._token = token
        self._private_key = private_key
        self._renew_at = renew_at
        self._space_rev = space_rev

        self._headers: t.Dict[str, t.Dict[str, str]] = {}

    @classmethod
    def parse(
        cls, token: str, private_key: 'EllipticCurvePrivateKey', space_rev: t.Optional[str] = None
    ) -> 'SpaceCredential':
        """Parse a space credential that was requested for the given key.

        Note:
            The signature of the credential is not verified. The hosts of the repos verify it.

        Args:
            token: Space credential.
            private_key: P-256 private key that the credential was requested for.
            space_rev: Revision of the space when the credential was issued.

        Returns:
            :obj:`SpaceCredential`: Space credential.

        Raises:
            :class:`atproto_space.exceptions.SpaceTokenError`: The token is not a space credential bound to the key.
        """
        space_token = parse_space_token('credential', token)
        if space_token.key_id != private_key_to_did_key(private_key):
            raise SpaceTokenError('Space credential is not bound to the requested key', 'BadJwtCnf')

        # renew a minute before the expiration, but not earlier than halfway through the lifetime
        margin = min(_RENEWAL_MARGIN, (space_token.exp - t.cast('float', space_token.iat)) / 2)

        return cls(token, private_key, space_token.exp - margin, space_rev)

    @property
    def token(self) -> str:
        """Space credential."""
        return self._token

    @property
    def renew_at(self) -> float:
        """Unix timestamp after which the credential should be renewed."""
        return self._renew_at

    @property
    def space_rev(self) -> t.Optional[str]:
        """Revision of the space when the credential was issued, if the space had any update.

        A reader that last saw an earlier revision has missed updates of the space.
        """
        return self._space_rev

    @property
    def needs_renewal(self) -> bool:
        """Tell whether the credential should be renewed."""
        return time.time() >= self._renew_at

    def headers(self, audience: str) -> t.Dict[str, str]:
        """Get the headers that present the credential to a host.

        Args:
            audience: DID of the repo for the methods of a repo, DID of the space authority for the methods of a space.

        Returns:
            :obj:`dict`: Authorization, audience and signature headers. They are created once per audience.
        """
        headers = self._headers.get(audience)
        if headers is None:
            headers = create_credential_headers(self._token, audience, self._private_key)
            self._headers[audience] = headers

        return dict(headers)
