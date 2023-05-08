##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


@dataclass
class Params(base.ParamsModelBase):

    """Parameters model for :obj:`app.bsky.feed.getPostThread`.

    Attributes:
        uri: Uri.
        depth: Depth.
    """

    uri: str
    depth: Optional[int] = None


@dataclass
class Response(base.ResponseModelBase):

    """Output data model for :obj:`app.bsky.feed.getPostThread`.

    Attributes:
        thread: Thread.
    """

    thread: Union[
        'models.AppBskyFeedDefs.ThreadViewPost',
        'models.AppBskyFeedDefs.NotFoundPost',
        'models.AppBskyFeedDefs.BlockedPost',
        'Dict[str, Any]',
    ]
