#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`internal.bsky.feed.getPosts`."""

    uris: t.List[string_formats.AtUri] = Field(max_length=200)  #: List of post AT-URIs to return hydrated views for.
    include3p_blocks: te.Annotated[
        t.Optional[bool],
        Field(validation_alias='include3pBlocks', serialization_alias='include3pBlocks', alias_priority=2),
    ] = None  #: Include quoted posts even when the quoting and quoted authors block each other, rather than replacing them with a blocked embed. For service-to-service moderation use only.
    include_takedowns: t.Optional[bool] = (
        False  #: Include taken-down posts in the response rather than omitting them. For service-to-service moderation use only.
    )


class ParamsDict(t.TypedDict):
    uris: t.List[string_formats.AtUri]  #: List of post AT-URIs to return hydrated views for.
    include3p_blocks: te.NotRequired[
        t.Optional[bool]
    ]  #: Include quoted posts even when the quoting and quoted authors block each other, rather than replacing them with a blocked embed. For service-to-service moderation use only.
    include_takedowns: te.NotRequired[
        t.Optional[bool]
    ]  #: Include taken-down posts in the response rather than omitting them. For service-to-service moderation use only.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`internal.bsky.feed.getPosts`."""

    posts: t.List['models.AppBskyFeedDefs.PostView']  #: Posts.
