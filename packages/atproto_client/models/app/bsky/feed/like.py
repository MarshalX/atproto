##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

from pydantic import Field

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Record(base.RecordModelBase):
    """Record model for :obj:`app.bsky.feed.like`."""

    created_at: str  #: Created at.
    subject: 'models.ComAtprotoRepoStrongRef.Main'  #: Subject.

    py_type: t.Literal['app.bsky.feed.like'] = Field(default='app.bsky.feed.like', alias='$type', frozen=True)


class GetRecordResponse(base.SugarResponseModelBase):
    """Get record response for :obj:`models.AppBskyFeedLike.Record`."""

    uri: str  #: The URI of the record.
    value: 'models.AppBskyFeedLike.Record'  #: The record.
    cid: t.Optional[str] = None  #: The CID of the record.


class ListRecordsResponse(base.SugarResponseModelBase):
    """List records response for :obj:`models.AppBskyFeedLike.Record`."""

    records: t.Dict[str, 'models.AppBskyFeedLike.Record']  #: Map of URIs to records.
    cursor: t.Optional[str] = None  #: Next page cursor.


class CreateRecordResponse(base.SugarResponseModelBase):
    """Create record response for :obj:`models.AppBskyFeedLike.Record`."""

    uri: str  #: The URI of the record.
    cid: str  #: The CID of the record.
