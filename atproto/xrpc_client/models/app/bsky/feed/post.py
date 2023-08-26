##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


class ReplyRef(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.post`."""

    parent: 'models.ComAtprotoRepoStrongRef.Main'  #: Parent.
    root: 'models.ComAtprotoRepoStrongRef.Main'  #: Root.

    py_type: te.Literal['app.bsky.feed.post#replyRef'] = Field(default='app.bsky.feed.post#replyRef', alias='$type')


class Entity(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.post`. Deprecated: use facets instead."""

    index: 'models.AppBskyFeedPost.TextSlice'  #: Index.
    type: str  #: Expected values are 'mention' and 'link'.
    value: str  #: Value.

    py_type: te.Literal['app.bsky.feed.post#entity'] = Field(default='app.bsky.feed.post#entity', alias='$type')


class TextSlice(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.post`. Deprecated. Use app.bsky.richtext instead -- A text segment. Start is inclusive, end is exclusive. Indices are for utf16-encoded strings."""

    end: int  #: End.
    start: int  #: Start.

    py_type: te.Literal['app.bsky.feed.post#textSlice'] = Field(default='app.bsky.feed.post#textSlice', alias='$type')


class Main(base.RecordModelBase):

    """Record model for :obj:`app.bsky.feed.post`."""

    createdAt: str  #: Created at.
    text: str  #: Text.
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
    ] = None  #: Deprecated: replaced by app.bsky.richtext.facet.
    facets: t.Optional[t.List['models.AppBskyRichtextFacet.Main']] = None  #: Facets.
    labels: t.Optional[
        te.Annotated[t.Union['models.ComAtprotoLabelDefs.SelfLabels'], Field(default=None, discriminator='py_type')]
    ] = None  #: Labels.
    langs: t.Optional[t.List[str]] = None  #: Langs.
    reply: t.Optional['models.AppBskyFeedPost.ReplyRef'] = None  #: Reply.

    py_type: te.Literal['app.bsky.feed.post'] = Field(default='app.bsky.feed.post', alias='$type')
