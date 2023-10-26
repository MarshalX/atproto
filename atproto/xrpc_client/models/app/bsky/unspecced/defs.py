##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing_extensions as te
from pydantic import Field

from atproto.xrpc_client.models import base


class SkeletonSearchPost(base.ModelBase):

    """Definition model for :obj:`app.bsky.unspecced.defs`."""

    uri: str  #: Uri.

    py_type: te.Literal['app.bsky.unspecced.defs#skeletonSearchPost'] = Field(
        default='app.bsky.unspecced.defs#skeletonSearchPost', alias='$type', frozen=True
    )


class SkeletonSearchActor(base.ModelBase):

    """Definition model for :obj:`app.bsky.unspecced.defs`."""

    did: str  #: Did.

    py_type: te.Literal['app.bsky.unspecced.defs#skeletonSearchActor'] = Field(
        default='app.bsky.unspecced.defs#skeletonSearchActor', alias='$type', frozen=True
    )
