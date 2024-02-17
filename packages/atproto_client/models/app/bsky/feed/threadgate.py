##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class MentionRule(base.ModelBase):
    """Definition model for :obj:`app.bsky.feed.threadgate`. Allow replies from actors mentioned in your post."""

    py_type: te.Literal['app.bsky.feed.threadgate#mentionRule'] = Field(
        default='app.bsky.feed.threadgate#mentionRule', alias='$type', frozen=True
    )


class FollowingRule(base.ModelBase):
    """Definition model for :obj:`app.bsky.feed.threadgate`. Allow replies from actors you follow."""

    py_type: te.Literal['app.bsky.feed.threadgate#followingRule'] = Field(
        default='app.bsky.feed.threadgate#followingRule', alias='$type', frozen=True
    )


class ListRule(base.ModelBase):
    """Definition model for :obj:`app.bsky.feed.threadgate`. Allow replies from actors on a list."""

    list: str  #: List.

    py_type: te.Literal['app.bsky.feed.threadgate#listRule'] = Field(
        default='app.bsky.feed.threadgate#listRule', alias='$type', frozen=True
    )


class Record(base.RecordModelBase):
    """Record model for :obj:`app.bsky.feed.threadgate`."""

    created_at: str  #: Created at.
    post: str  #: Reference (AT-URI) to the post record.
    allow: t.Optional[
        t.List[
            te.Annotated[
                t.Union[
                    'models.AppBskyFeedThreadgate.MentionRule',
                    'models.AppBskyFeedThreadgate.FollowingRule',
                    'models.AppBskyFeedThreadgate.ListRule',
                ],
                Field(discriminator='py_type'),
            ]
        ]
    ] = Field(default=None, max_length=5)  #: Allow.

    py_type: te.Literal['app.bsky.feed.threadgate'] = Field(
        default='app.bsky.feed.threadgate', alias='$type', frozen=True
    )


class Main(Record):
    def __init_subclass__(cls, **data: t.Any) -> None:
        import warnings

        warnings.warn('Main class is deprecated. Use Record class instead.', DeprecationWarning, stacklevel=2)
        super().__init_subclass__(**data)

    def __init__(self, **data: t.Any) -> None:
        import warnings

        warnings.warn('Main class is deprecated. Use Record class instead.', DeprecationWarning, stacklevel=2)
        super().__init__(**data)


class GetRecordResponse(base.SugarResponseModelBase):
    """Get record response for :obj:`models.AppBskyFeedThreadgate.Record`."""

    uri: str  #: The URI of the record.
    value: 'models.AppBskyFeedThreadgate.Record'  #: The record.
    cid: t.Optional[str] = None  #: The CID of the record.


class ListRecordsResponse(base.SugarResponseModelBase):
    """List records response for :obj:`models.AppBskyFeedThreadgate.Record`."""

    records: t.Dict[str, 'models.AppBskyFeedThreadgate.Record']  #: Map of URIs to records.
    cursor: t.Optional[str] = None  #: Next page cursor.


class CreateRecordResponse(base.SugarResponseModelBase):
    """Create record response for :obj:`models.AppBskyFeedThreadgate.Record`."""

    uri: str  #: The URI of the record.
    cid: str  #: The CID of the record.
