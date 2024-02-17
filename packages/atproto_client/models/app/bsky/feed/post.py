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


class ReplyRef(base.ModelBase):
    """Definition model for :obj:`app.bsky.feed.post`."""

    parent: 'models.ComAtprotoRepoStrongRef.Main'  #: Parent.
    root: 'models.ComAtprotoRepoStrongRef.Main'  #: Root.

    py_type: te.Literal['app.bsky.feed.post#replyRef'] = Field(
        default='app.bsky.feed.post#replyRef', alias='$type', frozen=True
    )


class Entity(base.ModelBase):
    """Definition model for :obj:`app.bsky.feed.post`. Deprecated: use facets instead."""

    index: 'models.AppBskyFeedPost.TextSlice'  #: Index.
    type: str  #: Expected values are 'mention' and 'link'.
    value: str  #: Value.

    py_type: te.Literal['app.bsky.feed.post#entity'] = Field(
        default='app.bsky.feed.post#entity', alias='$type', frozen=True
    )


class TextSlice(base.ModelBase):
    """Definition model for :obj:`app.bsky.feed.post`. Deprecated. Use app.bsky.richtext instead -- A text segment. Start is inclusive, end is exclusive. Indices are for utf16-encoded strings."""

    end: int = Field(ge=0)  #: End.
    start: int = Field(ge=0)  #: Start.

    py_type: te.Literal['app.bsky.feed.post#textSlice'] = Field(
        default='app.bsky.feed.post#textSlice', alias='$type', frozen=True
    )


class Record(base.RecordModelBase):
    """Record model for :obj:`app.bsky.feed.post`."""

    created_at: str  #: Client-declared timestamp when this post was originally created.
    text: str = Field(max_length=3000)  #: The primary post content. May be an empty string, if there are embeds.
    embed: t.Optional[
        te.Annotated[
            t.Union[
                'models.AppBskyEmbedImages.Main',
                'models.AppBskyEmbedExternal.Main',
                'models.AppBskyEmbedRecord.Main',
                'models.AppBskyEmbedRecordWithMedia.Main',
            ],
            Field(default=None, discriminator='py_type'),
        ]
    ] = None  #: Embed.
    entities: t.Optional[
        t.List['models.AppBskyFeedPost.Entity']
    ] = None  #: DEPRECATED: replaced by app.bsky.richtext.facet.
    facets: t.Optional[
        t.List['models.AppBskyRichtextFacet.Main']
    ] = None  #: Annotations of text (mentions, URLs, hashtags, etc).
    labels: t.Optional[
        te.Annotated[t.Union['models.ComAtprotoLabelDefs.SelfLabels'], Field(default=None, discriminator='py_type')]
    ] = None  #: Self-label values for this post. Effectively content warnings.
    langs: t.Optional[t.List[str]] = Field(
        default=None, max_length=3
    )  #: Indicates human language of post primary text content.
    reply: t.Optional['models.AppBskyFeedPost.ReplyRef'] = None  #: Reply.
    tags: t.Optional[t.List[str]] = Field(
        default=None, max_length=8
    )  #: Additional hashtags, in addition to any included in post text and facets.

    py_type: te.Literal['app.bsky.feed.post'] = Field(default='app.bsky.feed.post', alias='$type', frozen=True)


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
    """Get record response for :obj:`models.AppBskyFeedPost.Record`."""

    uri: str  #: The URI of the record.
    value: 'models.AppBskyFeedPost.Record'  #: The record.
    cid: t.Optional[str] = None  #: The CID of the record.


class ListRecordsResponse(base.SugarResponseModelBase):
    """List records response for :obj:`models.AppBskyFeedPost.Record`."""

    records: t.Dict[str, 'models.AppBskyFeedPost.Record']  #: Map of URIs to records.
    cursor: t.Optional[str] = None  #: Next page cursor.


class CreateRecordResponse(base.SugarResponseModelBase):
    """Create record response for :obj:`models.AppBskyFeedPost.Record`."""

    uri: str  #: The URI of the record.
    cid: str  #: The CID of the record.
