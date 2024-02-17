##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`app.bsky.feed.getPostThread`."""

    uri: str  #: Reference (AT-URI) to post record.
    depth: t.Optional[int] = Field(
        default=6, ge=0, le=1000
    )  #: How many levels of reply depth should be included in response.
    parent_height: t.Optional[int] = Field(
        default=80, ge=0, le=1000
    )  #: How many levels of parent (and grandparent, etc) post to include.


class ParamsDict(te.TypedDict):
    uri: str  #: Reference (AT-URI) to post record.
    depth: te.NotRequired[t.Optional[int]]  #: How many levels of reply depth should be included in response.
    parent_height: te.NotRequired[t.Optional[int]]  #: How many levels of parent (and grandparent, etc) post to include.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`app.bsky.feed.getPostThread`."""

    thread: te.Annotated[
        t.Union[
            'models.AppBskyFeedDefs.ThreadViewPost',
            'models.AppBskyFeedDefs.NotFoundPost',
            'models.AppBskyFeedDefs.BlockedPost',
        ],
        Field(discriminator='py_type'),
    ]  #: Thread.
