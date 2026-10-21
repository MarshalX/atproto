import hashlib
import typing as t
from datetime import datetime, timezone

import libipld
from atproto_client import models
from atproto_client.exceptions import ModelError
from atproto_client.models.base import ModelBase
from atproto_client.models.utils import get_or_create

from atproto_jetstream.archive.segment import (
    KIND_ACCOUNT,
    KIND_DELETE,
    KIND_IDENTITY,
    KIND_SYNC,
    SegmentEvent,
)
from atproto_jetstream.exceptions import JetstreamDecodingError
from atproto_jetstream.models import _is_json_object

#: The archive never carries #info advisories, so every archived event has a seq.
ArchivedEventsMessage = t.Union[
    models.NetworkBskyJetstreamSubscribeEvents.Commit,
    models.NetworkBskyJetstreamSubscribeEvents.Identity,
    models.NetworkBskyJetstreamSubscribeEvents.Account,
    models.NetworkBskyJetstreamSubscribeEvents.Sync,
]

#: CIDv1 + dag-cbor codec + sha2-256 multihash prefix. The block format has no CID column.
_CID_PREFIX = bytes([0x01, 0x71, 0x12, 0x20])

_MARKER_FIELD = {
    KIND_IDENTITY: 'identity',
    KIND_ACCOUNT: 'account',
    KIND_SYNC: 'sync',
}

_PayloadModelT = t.TypeVar('_PayloadModelT', bound=ModelBase)


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


def _decode_marker_payload(payload: bytes, model: t.Type[_PayloadModelT]) -> _PayloadModelT:
    decoded = libipld.decode_dag_cbor(payload)
    if not _is_json_object(decoded):
        raise JetstreamDecodingError('Marker row payload is not a map')

    try:
        return get_or_create(decoded, model)
    except ModelError as e:
        raise JetstreamDecodingError('Invalid marker row payload') from e


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

    field = _MARKER_FIELD.get(event.kind)
    if field is None:
        raise JetstreamDecodingError(f'Unknown row kind: {event.kind}')

    if event.payload is None:
        raise JetstreamDecodingError(f'{field} row carries no payload')

    upstream = models.ComAtprotoSyncSubscribeRepos
    if event.kind == KIND_IDENTITY:
        return models.NetworkBskyJetstreamSubscribeEvents.Identity(
            seq=event.seq,
            did=event.did,
            time=time,
            identity=_decode_marker_payload(event.payload, upstream.Identity),
        )

    if event.kind == KIND_ACCOUNT:
        return models.NetworkBskyJetstreamSubscribeEvents.Account(
            seq=event.seq,
            did=event.did,
            time=time,
            account=_decode_marker_payload(event.payload, upstream.Account),
        )

    return models.NetworkBskyJetstreamSubscribeEvents.Sync(
        seq=event.seq,
        did=event.did,
        time=time,
        sync=_decode_marker_payload(event.payload, upstream.Sync),
    )


def to_messages(events: t.Iterable[SegmentEvent], *, with_cid: bool = True) -> t.Iterator[ArchivedEventsMessage]:
    """Convert rows, skipping any that cannot be decoded."""
    for event in events:
        try:
            yield to_message(event, with_cid=with_cid)
        except (JetstreamDecodingError, ValueError):
            # one unreadable row must not end a sweep
            continue
