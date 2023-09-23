##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


class Params(base.ParamsModelBase):

    """Parameters model for :obj:`app.bsky.feed.getFeedGenerator`."""

    feed: str  #: Feed.


class ParamsDict(te.TypedDict):
    feed: str  #: Feed.


class Response(base.ResponseModelBase):

    """Output data model for :obj:`app.bsky.feed.getFeedGenerator`."""

    is_online: bool = Field(alias='isOnline')  #: Is online.
    is_valid: bool = Field(alias='isValid')  #: Is valid.
    view: 'models.AppBskyFeedDefs.GeneratorView'  #: View.
