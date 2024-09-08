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


class ProfileViewBasic(base.ModelBase):
    """Definition model for :obj:`chat.bsky.actor.defs`."""

    did: str  #: Did.
    handle: str  #: Handle.
    associated: t.Optional['models.AppBskyActorDefs.ProfileAssociated'] = None  #: Associated.
    avatar: t.Optional[str] = None  #: Avatar.
    chat_disabled: t.Optional[bool] = None  #: Set to true when the actor cannot actively participate in converations.
    display_name: t.Optional[str] = Field(default=None, max_length=640)  #: Display name.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.
    viewer: t.Optional['models.AppBskyActorDefs.ViewerState'] = None  #: Viewer.

    py_type: t.Literal['chat.bsky.actor.defs#profileViewBasic'] = Field(
        default='chat.bsky.actor.defs#profileViewBasic', alias='$type', frozen=True
    )
