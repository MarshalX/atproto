##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

from pydantic import Field

from atproto_client.models import base, string_formats


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
