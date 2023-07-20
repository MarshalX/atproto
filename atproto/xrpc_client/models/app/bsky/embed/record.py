##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t
from dataclasses import dataclass

from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


@dataclass
class Main(base.ModelBase):

    """Definition model for :obj:`app.bsky.embed.record`."""

    record: 'models.ComAtprotoRepoStrongRef.Main'  #: Record.

    _type: str = 'app.bsky.embed.record'


@dataclass
class View(base.ModelBase):

    """Definition model for :obj:`app.bsky.embed.record`."""

    record: t.Union[
        'models.AppBskyEmbedRecord.ViewRecord',
        'models.AppBskyEmbedRecord.ViewNotFound',
        'models.AppBskyEmbedRecord.ViewBlocked',
        'models.AppBskyFeedDefs.GeneratorView',
        'models.AppBskyGraphDefs.ListView',
        't.Dict[str, t.Any]',
    ]  #: Record.

    _type: str = 'app.bsky.embed.record#view'


@dataclass
class ViewRecord(base.ModelBase):

    """Definition model for :obj:`app.bsky.embed.record`."""

    author: 'models.AppBskyActorDefs.ProfileViewBasic'  #: Author.
    cid: str  #: Cid.
    indexedAt: str  #: Indexed at.
    uri: str  #: Uri.
    value: 'base.UnknownDict'  #: Value.
    embeds: t.Optional[
        t.List[
            t.Union[
                'models.AppBskyEmbedImages.View',
                'models.AppBskyEmbedExternal.View',
                'models.AppBskyEmbedRecord.View',
                'models.AppBskyEmbedRecordWithMedia.View',
                't.Dict[str, t.Any]',
            ]
        ]
    ] = None  #: Embeds.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.

    _type: str = 'app.bsky.embed.record#viewRecord'


@dataclass
class ViewNotFound(base.ModelBase):

    """Definition model for :obj:`app.bsky.embed.record`."""

    uri: str  #: Uri.

    _type: str = 'app.bsky.embed.record#viewNotFound'


@dataclass
class ViewBlocked(base.ModelBase):

    """Definition model for :obj:`app.bsky.embed.record`."""

    uri: str  #: Uri.

    _type: str = 'app.bsky.embed.record#viewBlocked'
