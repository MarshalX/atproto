##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`app.bsky.feed.getFeedGenerator`."""

    feed: str  #: AT-URI of the feed generator record.


class ParamsDict(te.TypedDict):
    feed: str  #: AT-URI of the feed generator record.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`app.bsky.feed.getFeedGenerator`."""

    is_online: (
        bool
    )  #: Indicates whether the feed generator service has been online recently, or else seems to be inactive.
    is_valid: bool  #: Indicates whether the feed generator service is compatible with the record declaration.
    view: 'models.AppBskyFeedDefs.GeneratorView'  #: View.
