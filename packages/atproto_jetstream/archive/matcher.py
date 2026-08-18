import typing as t

from atproto_jetstream.archive.segment import KIND_ACCOUNT, KIND_IDENTITY, KIND_SYNC, SegmentEvent

_KIND_NAME = {
    KIND_IDENTITY: 'identity',
    KIND_ACCOUNT: 'account',
    KIND_SYNC: 'sync',
}

_COMMIT_KIND = 'commit'

_WILDCARD_SUFFIX = '.*'


class RowMatcher:
    """Exact row filter over decoded segment rows.

    The plan only narrows which blocks are downloaded: it works on whole blocks and coarse
    collection ids, so a downloaded block carries rows the caller never asked for. This is
    the authority on what is delivered.

    Args:
        kinds: Event kinds to keep. Empty means all.
        dids: Repo DIDs to keep. Empty means all.
        collections: Collection NSIDs or `<prefix>.*` patterns. Empty means all.
        after_seq: Exclusive lower bound.
        before_seq: Inclusive upper bound.
    """

    def __init__(
        self,
        kinds: t.Optional[t.Sequence[str]] = None,
        dids: t.Optional[t.Sequence[str]] = None,
        collections: t.Optional[t.Sequence[str]] = None,
        after_seq: int = 0,
        before_seq: t.Optional[int] = None,
    ) -> None:
        self._kinds = frozenset(kinds or ())
        self._dids = frozenset(dids or ())
        self._after_seq = after_seq
        self._before_seq = before_seq

        exact, prefixes = set(), []
        for pattern in collections or ():
            if pattern.endswith(_WILDCARD_SUFFIX):
                prefixes.append(pattern[: -len(_WILDCARD_SUFFIX)])
            else:
                exact.add(pattern)

        self._collections = frozenset(exact)
        self._collection_prefixes = tuple(prefixes)

    def advance_to(self, seq: int) -> None:
        """Raise the seq floor after a resume, so a straddling block does not re-emit rows."""
        self._after_seq = max(self._after_seq, seq)

    def matches(self, event: SegmentEvent) -> bool:
        """Whether the row should be delivered."""
        if event.seq <= self._after_seq:
            return False

        if self._before_seq is not None and event.seq > self._before_seq:
            return False

        if self._dids and event.did not in self._dids:
            return False

        if self._kinds and self._kind_name(event) not in self._kinds:
            return False

        # collections constrain commits only: identity, account and sync are the only purge
        # signals a folding consumer gets, so they survive a collection filter
        if not event.is_commit:
            return True

        return self._matches_collection(event.collection)

    def _matches_collection(self, collection: str) -> bool:
        if not self._collections and not self._collection_prefixes:
            return True

        if collection in self._collections:
            return True

        return any(collection.startswith(prefix) for prefix in self._collection_prefixes)

    @staticmethod
    def _kind_name(event: SegmentEvent) -> str:
        if event.is_commit:
            return _COMMIT_KIND

        return _KIND_NAME.get(event.kind, '')

    def filter(self, events: t.Iterable[SegmentEvent]) -> t.Iterator[SegmentEvent]:
        """Yield only the rows that match."""
        return (event for event in events if self.matches(event))
