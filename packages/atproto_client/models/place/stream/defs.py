#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

from pydantic import Field

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class BlockView(base.ModelBase):
    """Definition model for :obj:`place.stream.defs`."""

    blocker: 'models.AppBskyActorDefs.ProfileViewBasic'  #: Blocker.
    cid: string_formats.Cid  #: Cid.
    indexed_at: string_formats.DateTime  #: Indexed at.
    record: 'models.AppBskyGraphBlock.Record'  #: Record.
    uri: string_formats.AtUri  #: Uri.

    py_type: t.Literal['place.stream.defs#blockView'] = Field(
        default='place.stream.defs#blockView', alias='$type', frozen=True
    )


class Rendition(base.ModelBase):
    """Definition model for :obj:`place.stream.defs`."""

    name: str  #: Name.

    py_type: t.Literal['place.stream.defs#rendition'] = Field(
        default='place.stream.defs#rendition', alias='$type', frozen=True
    )


class Renditions(base.ModelBase):
    """Definition model for :obj:`place.stream.defs`."""

    renditions: t.List['models.PlaceStreamDefs.Rendition']  #: Renditions.

    py_type: t.Literal['place.stream.defs#renditions'] = Field(
        default='place.stream.defs#renditions', alias='$type', frozen=True
    )


class ActivityGame(base.ModelBase):
    """Definition model for :obj:`place.stream.defs`. A game from the gamesgamesgamesgames catalog, identified by its AT URI."""

    uri: string_formats.AtUri  #: Uri.
    name: t.Optional[str] = None  #: Cached display name of the game.

    py_type: t.Literal['place.stream.defs#activityGame'] = Field(
        default='place.stream.defs#activityGame', alias='$type', frozen=True
    )


class ActivityLabel(base.ModelBase):
    """Definition model for :obj:`place.stream.defs`. A non-game activity with a well-known label."""

    label: t.Union[
        t.Literal[
            'events',
            'just_chatting',
            'podcasting',
            'music',
            'art',
            'software_dev',
            'cooking',
            'miniatures',
            'makers_crafting',
            'fitness',
            'sports',
        ],
        str,
    ]  #: Label.

    py_type: t.Literal['place.stream.defs#activityLabel'] = Field(
        default='place.stream.defs#activityLabel', alias='$type', frozen=True
    )
