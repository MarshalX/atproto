import typing as t
from dataclasses import dataclass, field

import typing_extensions as te

if t.TYPE_CHECKING:
    from atproto_client import models
    from atproto_client.exceptions import ModelError
    from atproto_client.models.dot_dict import DotDict

#: Latest update of a repo in the writer set of a space: its latest write, or its removal from the set.
Writer: te.TypeAlias = t.Union['models.ComAtprotoSpaceDefs.RepoWrite', 'models.ComAtprotoSpaceDefs.RepoRemoved']

#: Policy that governs a space: one of the policies that every PDS supports, or one that only its host knows.
SpacePolicy: te.TypeAlias = t.Union[
    'models.ComAtprotoPersonalspacePolicy.Main',
    'models.ComAtprotoMemberspacePolicy.Main',
    'models.ComAtprotoManagedspacePolicy.Main',
    'DotDict',
]

#: Operation of a batch of writes to a repo in a space.
WriteOperation: te.TypeAlias = t.Union[
    'models.ComAtprotoSpaceApplyWrites.Create',
    'models.ComAtprotoSpaceApplyWrites.Update',
    'models.ComAtprotoSpaceApplyWrites.Delete',
]


@dataclass(frozen=True)
class RepoRecord:
    """Record of a repo in a space.

    Attributes:
        collection: NSID of the record collection.
        rkey: Record key.
        cid: CID of the record.
        value: Record as decoded from DAG-CBOR. A link is a :obj:`atproto_core.cid.CID`.
    """

    collection: str
    rkey: str
    cid: str
    value: t.Dict[str, t.Any]


@dataclass(frozen=True)
class RepoHead:
    """State of a repo in a space as a syncer knows it. The state to sync the repo from later.

    Attributes:
        rev: Revision of the commit that the state matches.
        state: State of the set hash of the records. See :obj:`atproto_space.commit.RepoCommit`.
    """

    rev: str
    state: bytes = field(repr=False)


@dataclass(frozen=True)
class RecordChange:
    """Change of a record of a repo in a space since a known state.

    Attributes:
        collection: NSID of the record collection.
        rkey: Record key.
        cid: CID of the record after the change. :obj:`None` when the record was deleted.
        prev: CID of the record before the change. :obj:`None` when the record was created.
        value: Record as decoded from DAG-CBOR, unless it was deleted. A link is a :obj:`atproto_core.cid.CID`.
    """

    collection: str
    rkey: str
    cid: t.Optional[str]
    prev: t.Optional[str]
    value: t.Optional[t.Dict[str, t.Any]] = None


@dataclass(frozen=True)
class RepoSnapshot:
    """Repo of a space in full, verified against its commit.

    Attributes:
        commit: Commit of the repo.
        head: State to sync the repo from later.
        records: Records of the repo in the order of their paths.
    """

    commit: 'models.ComAtprotoSpaceDefs.Commit'
    head: RepoHead
    records: t.List[RepoRecord]


@dataclass(frozen=True)
class RepoChanges:
    """Changes of a repo of a space since a known state, verified against its commit.

    Attributes:
        commit: Commit of the repo.
        head: State to sync the repo from later.
        changes: Changes since the known state, one for each record that changed.
    """

    commit: 'models.ComAtprotoSpaceDefs.Commit'
    head: RepoHead
    changes: t.List[RecordChange]


@dataclass(frozen=True)
class SpaceRecord:
    """Record of a space, flagged with whether it is valid.

    A record is valid when its type is the collection it is stored under, the type of the space declares
    the collection, and the record matches the model of the collection.

    Attributes:
        repo: DID of the account that the record belongs to.
        collection: NSID of the record collection.
        rkey: Record key.
        cid: CID of the record.
        value: Record model, or :obj:`atproto_client.models.dot_dict.DotDict` for a collection without a model.
            An invalid record has the value that its host returned, if any. A value that is not a model
            is in the JSON form when it was listed, and as decoded from DAG-CBOR when its repo was read in full,
            so a link is then a :obj:`atproto_core.cid.CID`.
        valid: Whether the record is valid.
        error: Reason why the record is invalid.
    """

    repo: str
    collection: str
    rkey: str
    cid: str
    value: t.Any
    valid: bool
    error: t.Optional['ModelError'] = None
