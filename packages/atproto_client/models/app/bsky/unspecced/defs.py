##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

from pydantic import Field

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class SkeletonSearchPost(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.defs`."""

    uri: string_formats.AtUri  #: Uri.

    py_type: t.Literal['app.bsky.unspecced.defs#skeletonSearchPost'] = Field(
        default='app.bsky.unspecced.defs#skeletonSearchPost', alias='$type', frozen=True
    )


class SkeletonSearchActor(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.defs`."""

    did: string_formats.Did  #: Did.

    py_type: t.Literal['app.bsky.unspecced.defs#skeletonSearchActor'] = Field(
        default='app.bsky.unspecced.defs#skeletonSearchActor', alias='$type', frozen=True
    )


class SkeletonSearchStarterPack(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.defs`."""

    uri: string_formats.AtUri  #: Uri.

    py_type: t.Literal['app.bsky.unspecced.defs#skeletonSearchStarterPack'] = Field(
        default='app.bsky.unspecced.defs#skeletonSearchStarterPack', alias='$type', frozen=True
    )


class TrendingTopic(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.defs`."""

    link: str  #: Link.
    topic: str  #: Topic.
    description: t.Optional[str] = None  #: Description.
    display_name: t.Optional[str] = None  #: Display name.

    py_type: t.Literal['app.bsky.unspecced.defs#trendingTopic'] = Field(
        default='app.bsky.unspecced.defs#trendingTopic', alias='$type', frozen=True
    )


class SkeletonTrend(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.defs`."""

    dids: t.List[string_formats.Did]  #: Dids.
    display_name: str  #: Display name.
    link: str  #: Link.
    post_count: int  #: Post count.
    started_at: string_formats.DateTime  #: Started at.
    topic: str  #: Topic.
    category: t.Optional[str] = None  #: Category.
    status: t.Optional[t.Union[t.Literal['hot'], str]] = None  #: Status.

    py_type: t.Literal['app.bsky.unspecced.defs#skeletonTrend'] = Field(
        default='app.bsky.unspecced.defs#skeletonTrend', alias='$type', frozen=True
    )


class TrendView(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.defs`."""

    actors: t.List['models.AppBskyActorDefs.ProfileViewBasic']  #: Actors.
    display_name: str  #: Display name.
    link: str  #: Link.
    post_count: int  #: Post count.
    started_at: string_formats.DateTime  #: Started at.
    topic: str  #: Topic.
    category: t.Optional[str] = None  #: Category.
    status: t.Optional[t.Union[t.Literal['hot'], str]] = None  #: Status.

    py_type: t.Literal['app.bsky.unspecced.defs#trendView'] = Field(
        default='app.bsky.unspecced.defs#trendView', alias='$type', frozen=True
    )
