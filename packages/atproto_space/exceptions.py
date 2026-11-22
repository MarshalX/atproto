from atproto_core.exceptions import AtProtocolError


class SpaceError(AtProtocolError):
    """Base exception for Spaces errors."""


class SpaceTokenError(SpaceError):
    """A delegation token, a space credential or a client attestation is malformed.

    Attributes:
        code: Reason, one of ``BadJwt``, ``BadJwtType``, ``BadJwtIss``, ``BadJwtSub``, ``BadJwtAudience``
            and ``BadJwtCnf``.
    """

    def __init__(self, message: str, code: str = 'BadJwt') -> None:
        super().__init__(message)
        self.code = code


class SpaceMacError(SpaceError):
    """The MAC of a response is missing, malformed or wrong."""


class SpaceRepoVerificationError(SpaceError):
    """A record, a commit, a repo or a blob failed verification."""


class SpaceIdentityError(SpaceError):
    """A DID document has no PDS endpoint or no usable ``#atproto_kem`` key."""


class RepoGapError(SpaceError):
    """A repo can not be synced from the known state."""
