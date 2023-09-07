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
    from atproto.xrpc_client.models.unknown_type import UnknownType
from atproto.xrpc_client.models import base


class Main(base.ModelBase):

    """Definition model for :obj:`app.bsky.embed.record`."""

    record: 'models.ComAtprotoRepoStrongRef.Main'  #: Record.

    py_type: te.Literal['app.bsky.embed.record'] = Field(default='app.bsky.embed.record', alias='$type', frozen=True)


class View(base.ModelBase):

    """Definition model for :obj:`app.bsky.embed.record`."""

    record: te.Annotated[
        t.Union[
            'models.AppBskyEmbedRecord.ViewRecord',
            'models.AppBskyEmbedRecord.ViewNotFound',
            'models.AppBskyEmbedRecord.ViewBlocked',
            'models.AppBskyFeedDefs.GeneratorView',
            'models.AppBskyGraphDefs.ListView',
        ],
        Field(discriminator='py_type'),
    ]  #: Record.

    py_type: te.Literal['app.bsky.embed.record#view'] = Field(
        default='app.bsky.embed.record#view', alias='$type', frozen=True
    )


class ViewRecord(base.ModelBase):

    """Definition model for :obj:`app.bsky.embed.record`."""

    author: 'models.AppBskyActorDefs.ProfileViewBasic'  #: Author.
    cid: str  #: Cid.
    indexed_at: str = Field(alias='indexedAt')  #: Indexed at.
    uri: str  #: Uri.
    value: 'UnknownType'  #: Value.
    embeds: t.Optional[
        t.List[
            te.Annotated[
                t.Union[
                    'models.AppBskyEmbedImages.View',
                    'models.AppBskyEmbedExternal.View',
                    'models.AppBskyEmbedRecord.View',
                    'models.AppBskyEmbedRecordWithMedia.View',
                ],
                Field(discriminator='py_type'),
            ]
        ]
    ] = None  #: Embeds.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.

    py_type: te.Literal['app.bsky.embed.record#viewRecord'] = Field(
        default='app.bsky.embed.record#viewRecord', alias='$type', frozen=True
    )


class ViewNotFound(base.ModelBase):

    """Definition model for :obj:`app.bsky.embed.record`."""

    not_found: bool = Field(alias='notFound', frozen=True)  #: Not found.
    uri: str  #: Uri.

    py_type: te.Literal['app.bsky.embed.record#viewNotFound'] = Field(
        default='app.bsky.embed.record#viewNotFound', alias='$type', frozen=True
    )


class ViewBlocked(base.ModelBase):

    """Definition model for :obj:`app.bsky.embed.record`."""

    author: 'models.AppBskyFeedDefs.BlockedAuthor'  #: Author.
    blocked: bool = Field(frozen=True)  #: Blocked.
    uri: str  #: Uri.

    py_type: te.Literal['app.bsky.embed.record#viewBlocked'] = Field(
        default='app.bsky.embed.record#viewBlocked', alias='$type', frozen=True
    )
