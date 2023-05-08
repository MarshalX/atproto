##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


@dataclass
class ReplyRef(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.post`.

    Attributes:
        root: Root.
        parent: Parent.
    """

    parent: 'models.ComAtprotoRepoStrongRef.Main'
    root: 'models.ComAtprotoRepoStrongRef.Main'


@dataclass
class Entity(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.post`. Deprecated: use facets instead.

    Attributes:
        index: Index.
        type: Expected values are 'mention' and 'link'.
        value: Value.
    """

    index: 'models.AppBskyFeedPost.TextSlice'
    type: str
    value: str


@dataclass
class TextSlice(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.post`. Deprecated. Use app.bsky.richtext instead -- A text segment. Start is inclusive, end is exclusive. Indices are for utf16-encoded strings.

    Attributes:
        start: Start.
        end: End.
    """

    end: int
    start: int


@dataclass
class Main(base.RecordModelBase):

    """Record model for :obj:`app.bsky.feed.post`.

    Attributes:
        text: Text.
        entities: Deprecated: replaced by app.bsky.richtext.facet.
        facets: Facets.
        reply: Reply.
        embed: Embed.
        createdAt: Created at.
    """

    createdAt: str
    text: str
    embed: Optional[
        Union[
            'models.AppBskyEmbedImages.Main',
            'models.AppBskyEmbedExternal.Main',
            'models.AppBskyEmbedRecord.Main',
            'models.AppBskyEmbedRecordWithMedia.Main',
            'Dict[str, Any]',
        ]
    ] = None
    entities: Optional[List['models.AppBskyFeedPost.Entity']] = None
    facets: Optional[List['models.AppBskyRichtextFacet.Main']] = None
    reply: Optional['models.AppBskyFeedPost.ReplyRef'] = None

    _type: str = 'app.bsky.feed.post'
