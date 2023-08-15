##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

if t.TYPE_CHECKING:
    from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


class ReplyRef(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.post`."""

    parent: 'models.ComAtprotoRepoStrongRef.Main'  #: Parent.
    root: 'models.ComAtprotoRepoStrongRef.Main'  #: Root.

    _type: str = 'app.bsky.feed.post#replyRef'


class Entity(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.post`. Deprecated: use facets instead."""

    index: 'models.AppBskyFeedPost.TextSlice'  #: Index.
    type: str  #: Expected values are 'mention' and 'link'.
    value: str  #: Value.

    _type: str = 'app.bsky.feed.post#entity'


class TextSlice(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.post`. Deprecated. Use app.bsky.richtext instead -- A text segment. Start is inclusive, end is exclusive. Indices are for utf16-encoded strings."""

    end: int  #: End.
    start: int  #: Start.

    _type: str = 'app.bsky.feed.post#textSlice'


class Main(base.RecordModelBase):

    """Record model for :obj:`app.bsky.feed.post`."""

    createdAt: str  #: Created at.
    text: str  #: Text.
    embed: t.Optional[
        t.Union[
            'models.AppBskyEmbedImages.Main',
            'models.AppBskyEmbedExternal.Main',
            'models.AppBskyEmbedRecord.Main',
            'models.AppBskyEmbedRecordWithMedia.Main',
            't.Dict[str, t.Any]',
        ]
    ] = None  #: Embed.
    entities: t.Optional[
        t.List['models.AppBskyFeedPost.Entity']
    ] = None  #: Deprecated: replaced by app.bsky.richtext.facet.
    facets: t.Optional[t.List['models.AppBskyRichtextFacet.Main']] = None  #: Facets.
    labels: t.Optional[t.Union['models.ComAtprotoLabelDefs.SelfLabels', 't.Dict[str, t.Any]']] = None  #: Labels.
    langs: t.Optional[t.List[str]] = None  #: Langs.
    reply: t.Optional['models.AppBskyFeedPost.ReplyRef'] = None  #: Reply.

    _type: str = 'app.bsky.feed.post'
