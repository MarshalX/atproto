import typing as t

from atproto_client import models
from atproto_client.exceptions import ModelError
from atproto_client.models.utils import get_or_create
from atproto_core.cbor import decode_dag
from atproto_core.exceptions import DAGCBORDecodingError
from atproto_core.nsid import validate_nsid
from atproto_core.star import STAR
from atproto_core.uri.space import is_record_key

from atproto_space._data import get_record_cid
from atproto_space.commit import COMMIT_VERSION, RepoCommit
from atproto_space.exceptions import SpaceRepoVerificationError
from atproto_space.models import RepoRecord

REPO_ARCHIVE_TYPE: t.Final = 'atproto-space-repo'

_MAX_META_LENGTH: t.Final = 64 * 1024
_MAX_KEY_LENGTH: t.Final = 4 * 1024
_MAX_VALUE_LENGTH: t.Final = 1024 * 1024

_TYPE_KEY: t.Final = '$type'


def _parse_meta(meta: t.Mapping[str, t.Any]) -> 'models.ComAtprotoSpaceDefs.Commit':
    if meta.get(_TYPE_KEY) != REPO_ARCHIVE_TYPE:
        raise SpaceRepoVerificationError(f'Invalid repo metadata: expected type {REPO_ARCHIVE_TYPE}')

    # the type names the archive, the rest of the metadata is the commit
    commit = {key: value for key, value in meta.items() if key != _TYPE_KEY}
    try:
        return get_or_create(commit, models.ComAtprotoSpaceDefs.Commit)
    except ModelError as e:
        raise SpaceRepoVerificationError('Invalid repo metadata') from e


def _parse_record_path(key: bytes) -> t.Tuple[str, str]:
    try:
        path = key.decode('utf-8')
    except UnicodeDecodeError as e:
        raise SpaceRepoVerificationError(f'Invalid record path: {key!r}') from e

    parts = path.split('/')
    if len(parts) != 2:
        raise SpaceRepoVerificationError(f'Invalid record path: {path}')

    collection, rkey = parts
    if not validate_nsid(collection, soft_fail=True):
        raise SpaceRepoVerificationError(f'Invalid NSID in record path: {path}')

    if not is_record_key(rkey):
        raise SpaceRepoVerificationError(f'Invalid record key in record path: {path}')

    return collection, rkey


def read_repo_archive(data: bytes) -> t.Tuple[STAR, 'models.ComAtprotoSpaceDefs.Commit']:
    """Read the archive of a repo.

    Note:
        The commit and the records are not verified yet. See :func:`atproto_space.commit.verify_commit`
        and :func:`verify_repo_archive_records`.

    Args:
        data: Content of the STAR file. For example, the response of `client.com.atproto.space.get_repo`.

    Returns:
        :obj:`tuple` of :obj:`atproto_core.star.STAR`, :obj:`models.ComAtprotoSpaceDefs.Commit`:
        Archive and the commit that its metadata holds.

    Raises:
        :class:`atproto.exceptions.InvalidStarError`: Invalid STAR file.
        :class:`atproto_space.exceptions.SpaceRepoVerificationError`: The metadata is not a commit
            of a supported version.
    """
    archive = STAR.from_bytes(
        data,
        max_meta_length=_MAX_META_LENGTH,
        max_key_length=_MAX_KEY_LENGTH,
        max_value_length=_MAX_VALUE_LENGTH,
    )

    commit = _parse_meta(archive.meta)
    if commit.ver != COMMIT_VERSION:
        raise SpaceRepoVerificationError(f'Unsupported commit version: {commit.ver}')

    return archive, commit


def _verify_records(
    archive: STAR, commit: 'models.ComAtprotoSpaceDefs.Commit'
) -> t.Tuple[t.List[RepoRecord], RepoCommit]:
    """Verify the records of a repo archive. Returns them together with the set hash that they add up to."""
    repo_commit = RepoCommit()
    records: t.List[RepoRecord] = []
    prev_key: t.Optional[bytes] = None

    for key, value in archive.pairs:
        collection, rkey = _parse_record_path(key)
        path = f'{collection}/{rkey}'

        if prev_key is not None and key <= prev_key:
            raise SpaceRepoVerificationError(f'Records out of order at {path}')

        prev_key = key

        try:
            record = decode_dag(value, canonical=True)
        except DAGCBORDecodingError as e:
            raise SpaceRepoVerificationError(f'Invalid record at {path}') from e

        # the bytes are hashed as received
        cid = get_record_cid(value)
        repo_commit.add(collection, rkey, cid)
        records.append(RepoRecord(collection=collection, rkey=rkey, cid=cid, value=record))

    if not repo_commit.matches(commit):
        raise SpaceRepoVerificationError('Records do not match the commit data')

    return records, repo_commit


def verify_repo_archive_records(archive: STAR, commit: 'models.ComAtprotoSpaceDefs.Commit') -> t.List[RepoRecord]:
    """Verify that the records of a repo archive are the ones that the commit describes.

    Note:
        The commit is not verified. See :func:`atproto_space.commit.verify_commit`.

    Args:
        archive: Archive of the repo.
        commit: Commit of the repo.

    Returns:
        :obj:`list` of :obj:`atproto_space.models.RepoRecord`: Records of the repo in the order of the archive.

    Raises:
        :class:`atproto_space.exceptions.SpaceRepoVerificationError`: A record is malformed or out of order,
            or the records are not the ones that the commit describes.
    """
    records, _ = _verify_records(archive, commit)

    return records
