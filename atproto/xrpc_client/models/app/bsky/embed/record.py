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
class Main(base.ModelBase):

    """Definition model for :obj:`app.bsky.embed.record`.

    Attributes:
        record: Record.
    """

    record: 'models.ComAtprotoRepoStrongRef.Main'

    _type: str = 'app.bsky.embed.record'


@dataclass
class View(base.ModelBase):

    """Definition model for :obj:`app.bsky.embed.record`.

    Attributes:
        record: Record.
    """

    record: Union[
        'models.AppBskyEmbedRecord.ViewRecord',
        'models.AppBskyEmbedRecord.ViewNotFound',
        'models.AppBskyEmbedRecord.ViewBlocked',
        'Dict[str, Any]',
    ]


@dataclass
class ViewRecord(base.ModelBase):

    """Definition model for :obj:`app.bsky.embed.record`.

    Attributes:
        uri: Uri.
        cid: Cid.
        author: Author.
        value: Value.
        labels: Labels.
        embeds: Embeds.
        indexedAt: Indexed at.
    """

    author: 'models.AppBskyActorDefs.ProfileViewBasic'
    cid: str
    indexedAt: str
    uri: str
    value: 'base.RecordModelBase'
    embeds: Optional[
        List[
            Union[
                'models.AppBskyEmbedImages.View',
                'models.AppBskyEmbedExternal.View',
                'models.AppBskyEmbedRecord.View',
                'models.AppBskyEmbedRecordWithMedia.View',
                'Dict[str, Any]',
            ]
        ]
    ] = None
    labels: Optional[List['models.ComAtprotoLabelDefs.Label']] = None


@dataclass
class ViewNotFound(base.ModelBase):

    """Definition model for :obj:`app.bsky.embed.record`.

    Attributes:
        uri: Uri.
    """

    uri: str


@dataclass
class ViewBlocked(base.ModelBase):

    """Definition model for :obj:`app.bsky.embed.record`.

    Attributes:
        uri: Uri.
    """

    uri: str
