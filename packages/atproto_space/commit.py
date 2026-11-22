import typing as t

from atproto_client.models.string_formats import TID_RE
from atproto_crypto.lthash import LtHash

from atproto_space.exceptions import SpaceRepoVerificationError

if t.TYPE_CHECKING:
    from atproto_client import models

    from atproto_space.models import RepoRecord

COMMIT_VERSION: t.Final = 1

_DATA_SIZE: t.Final = 32


def _format_element(collection: str, rkey: str, cid: str) -> str:
    return f'{collection}/{rkey}/{cid}'


class RepoCommit:
    """Set hash of the records of a repo. The data of a commit is its digest.

    Args:
        state: State to continue from. The empty repo by default.
    """

    def __init__(self, state: t.Optional[bytes] = None) -> None:
        self._set_hash = LtHash(state)

    @classmethod
    def from_records(cls, records: t.Iterable['RepoRecord']) -> 'RepoCommit':
        """Create `RepoCommit` instance from the records of a repo."""
        commit = cls()
        for record in records:
            commit.add(record.collection, record.rkey, record.cid)

        return commit

    def add(self, collection: str, rkey: str, cid: str) -> None:
        """Add the record to the repo.

        Args:
            collection: NSID of the record collection.
            rkey: Record key.
            cid: CID of the record.
        """
        self._set_hash.add(_format_element(collection, rkey, cid))

    def remove(self, collection: str, rkey: str, cid: str) -> None:
        """Remove the record from the repo.

        Args:
            collection: NSID of the record collection.
            rkey: Record key.
            cid: CID of the record.
        """
        self._set_hash.remove(_format_element(collection, rkey, cid))

    def apply(self, collection: str, rkey: str, cid: t.Optional[str], prev: t.Optional[str]) -> None:
        """Apply the operation to the repo.

        Args:
            collection: NSID of the record collection.
            rkey: Record key.
            cid: CID of the record after the operation. :obj:`None` when the record is deleted.
            prev: CID of the record before the operation. :obj:`None` when the record is created.
        """
        if prev:
            self.remove(collection, rkey, prev)
        if cid:
            self.add(collection, rkey, cid)

    def matches(self, commit: 'models.ComAtprotoSpaceDefs.Commit') -> bool:
        """Tell whether the records of the repo are the ones that the commit describes.

        Note:
            The commit is not verified. On its own a match says nothing about where the records came from.

        Args:
            commit: Commit of the repo.

        Returns:
            :obj:`bool`: Whether the data of the commit is the digest of the records.
        """
        return self._set_hash.digest() == commit.data

    @property
    def state(self) -> bytes:
        """Get state of the set hash, which a later `RepoCommit` continues from."""
        return self._set_hash.state


def verify_commit(commit: 'models.ComAtprotoSpaceDefs.Commit', space: str, repo: str) -> None:
    """Verify that a commit is well-formed and describes the requested repo.

    Note:
        The commit is not authenticated. See :func:`atproto_space.mac.verify_commit_mac`.

    Args:
        commit: Commit to verify.
        space: URI of the space that was requested.
        repo: DID of the repo that was requested.

    Raises:
        :class:`atproto_space.exceptions.SpaceRepoVerificationError`: The commit has an unsupported version,
            describes another repo or another space, or is malformed.
    """
    if commit.ver != COMMIT_VERSION:
        raise SpaceRepoVerificationError(f'Unsupported commit version: {commit.ver}')

    if commit.repo != repo:
        raise SpaceRepoVerificationError(f'Commit is for another repo: {commit.repo}')

    if commit.space != space:
        raise SpaceRepoVerificationError(f'Commit is for another space: {commit.space}')

    if not TID_RE.fullmatch(commit.rev):
        raise SpaceRepoVerificationError(f'Commit revision is not a TID: {commit.rev}')

    if len(commit.data) != _DATA_SIZE:
        raise SpaceRepoVerificationError(f'Commit data must be {_DATA_SIZE} bytes, got {len(commit.data)}')
