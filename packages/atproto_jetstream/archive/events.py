import hashlib
import typing as t
from datetime import datetime, timezone

import libipld
from atproto_client import models
from atproto_client.models.utils import get_or_create

from atproto_jetstream.archive.segment import (
    KIND_ACCOUNT,
    KIND_DELETE,
    KIND_IDENTITY,
    KIND_SYNC,
    SegmentEvent,
)
from atproto_jetstream.exceptions import JetstreamDecodingError

#: The archive never carries #info advisories, so every archived event has a seq.
ArchivedEventsMessage = t.Union[
    models.NetworkBskyJetstreamSubscribeEvents.Commit,
    models.NetworkBskyJetstreamSubscribeEvents.Identity,
    models.NetworkBskyJetstreamSubscribeEvents.Account,
    models.NetworkBskyJetstreamSubscribeEvents.Sync,
]

#: CIDv1 + dag-cbor codec + sha2-256 multihash prefix. The block format has no CID column.
_CID_PREFIX = bytes([0x01, 0x71, 0x12, 0x20])

_MARKER_MODEL = {
    KIND_IDENTITY: (models.NetworkBskyJetstreamSubscribeEvents.Identity, 'identity'),
    KIND_ACCOUNT: (models.NetworkBskyJetstreamSubscribeEvents.Account, 'account'),
    KIND_SYNC: (models.NetworkBskyJetstreamSubscribeEvents.Sync, 'sync'),
}

_MARKER_PAYLOAD_MODEL = {
    KIND_IDENTITY: models.ComAtprotoSyncSubscribeRepos.Identity,
    KIND_ACCOUNT: models.ComAtprotoSyncSubscribeRepos.Account,
    KIND_SYNC: models.ComAtprotoSyncSubscribeRepos.Sync,
}


def compute_record_cid(payload: bytes) -> str:
    """Derive a record's CID from its DAG-CBOR bytes.

    Args:
        payload: Canonical DAG-CBOR of the record.

    Returns:
        :obj:`str`: CIDv1 string.
    """
    return libipld.encode_cid(_CID_PREFIX + hashlib.sha256(payload).digest())


def format_time_us(time_us: int) -> str:
    """Render a unix-microseconds timestamp the way the live wire does."""
    moment = datetime.fromtimestamp(time_us / 1_000_000, tz=timezone.utc)

    return f'{moment.strftime("%Y-%m-%dT%H:%M:%S.%f")}Z'


def to_message(event: SegmentEvent, *, with_cid: bool = True) -> ArchivedEventsMessage:
    """Convert a decoded segment row into the model the live tail delivers.

    A caller cannot tell whether an event arrived over the websocket or out of a segment.

    Args:
        event: Decoded segment row.
        with_cid: Derive the record CID. Skipping it saves a hash per record.

    Returns:
        :obj:`ArchivedEventsMessage`: Corresponding message model.

    Raises:
        :class:`atproto.exceptions.JetstreamDecodingError`: Unknown row kind or bad payload.
    """
    time = format_time_us(event.time_us)

    if event.is_commit:
        record = None
        cid = None
        if event.kind != KIND_DELETE and event.payload is not None:
            record = libipld.decode_dag_cbor(event.payload)
            if with_cid:
                cid = compute_record_cid(event.payload)

        return models.NetworkBskyJetstreamSubscribeEvents.Commit(
            seq=event.seq,
            did=event.did,
            time=time,
            rev=event.rev,
            operation=event.operation or '',
            collection=event.collection,
            rkey=event.rkey,
            record=record,
            cid=cid,
        )

    marker = _MARKER_MODEL.get(event.kind)
    if marker is None:
        raise JetstreamDecodingError(f'Unknown row kind: {event.kind}')

    model_class, field = marker
    if event.payload is None:
        raise JetstreamDecodingError(f'{field} row carries no payload')

    payload_model = get_or_create(libipld.decode_dag_cbor(event.payload), _MARKER_PAYLOAD_MODEL[event.kind])

    return model_class(seq=event.seq, did=event.did, time=time, **{field: payload_model})


def to_messages(events: t.Iterable[SegmentEvent], *, with_cid: bool = True) -> t.Iterator[ArchivedEventsMessage]:
    """Convert rows, skipping any that cannot be decoded."""
    for event in events:
        try:
            yield to_message(event, with_cid=with_cid)
        except (JetstreamDecodingError, ValueError):
            # one unreadable row must not end a sweep
            continue
