#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

from pydantic import Field

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base, unknown_union


class Main(base.ModelBase):
    """Definition model for :obj:`chat.bsky.embed.joinLink`."""

    code: str  #: The join link code.

    py_type: t.Literal['chat.bsky.embed.joinLink'] = Field(
        default='chat.bsky.embed.joinLink', alias='$type', frozen=True
    )


class View(base.ModelBase):
    """Definition model for :obj:`chat.bsky.embed.joinLink`."""

    join_link_preview: unknown_union.OpenUnion[
        t.Union[
            'models.ChatBskyGroupDefs.JoinLinkPreviewView',
            'models.ChatBskyGroupDefs.DisabledJoinLinkPreviewView',
            'models.ChatBskyGroupDefs.InvalidJoinLinkPreviewView',
        ]
    ]  #: Join link preview.

    py_type: t.Literal['chat.bsky.embed.joinLink#view'] = Field(
        default='chat.bsky.embed.joinLink#view', alias='$type', frozen=True
    )
