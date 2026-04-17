##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base

MemberRole = t.Union[t.Literal['owner'], t.Literal['standard'], str]  #: Member role


class ProfileViewBasic(base.ModelBase):
    """Definition model for :obj:`chat.bsky.actor.defs`."""

    did: string_formats.Did  #: Did.
    handle: string_formats.Handle  #: Handle.
    associated: t.Optional['models.AppBskyActorDefs.ProfileAssociated'] = None  #: Associated.
    avatar: t.Optional[string_formats.Uri] = None  #: Avatar.
    chat_disabled: t.Optional[bool] = None  #: Set to true when the actor cannot actively participate in conversations.
    created_at: t.Optional[string_formats.DateTime] = None  #: Created at.
    display_name: te.Annotated[t.Optional[str], Field(max_length=640)] = None  #: Display name.
    kind: t.Optional[
        te.Annotated[
            t.Union['models.ChatBskyActorDefs.DirectConvoMember', 'models.ChatBskyActorDefs.GroupConvoMember'],
            Field(discriminator='py_type'),
        ]
    ] = None  #: Union field that has data specific to different kinds of convos.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.
    verification: t.Optional['models.AppBskyActorDefs.VerificationState'] = None  #: Verification.
    viewer: t.Optional['models.AppBskyActorDefs.ViewerState'] = None  #: Viewer.

    py_type: t.Literal['chat.bsky.actor.defs#profileViewBasic'] = Field(
        default='chat.bsky.actor.defs#profileViewBasic', alias='$type', frozen=True
    )


class DirectConvoMember(base.ModelBase):
    """Definition model for :obj:`chat.bsky.actor.defs`. [NOTE: This is under active development and should be considered unstable while this note is here]."""

    py_type: t.Literal['chat.bsky.actor.defs#directConvoMember'] = Field(
        default='chat.bsky.actor.defs#directConvoMember', alias='$type', frozen=True
    )


class GroupConvoMember(base.ModelBase):
    """Definition model for :obj:`chat.bsky.actor.defs`. [NOTE: This is under active development and should be considered unstable while this note is here]."""

    role: 'models.ChatBskyActorDefs.MemberRole'  #: The member's role within this conversation. Only present in group conversation member lists.
    added_by: t.Optional['models.ChatBskyActorDefs.ProfileViewBasic'] = (
        None  #: Who added this member. Only present if the member was added (instead of joining via link).
    )

    py_type: t.Literal['chat.bsky.actor.defs#groupConvoMember'] = Field(
        default='chat.bsky.actor.defs#groupConvoMember', alias='$type', frozen=True
    )
