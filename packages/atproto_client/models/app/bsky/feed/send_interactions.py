##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Data(base.DataModelBase):
    """Input data model for :obj:`app.bsky.feed.sendInteractions`."""

    interactions: t.List['models.AppBskyFeedDefs.Interaction']  #: Interactions.
    feed: t.Optional[string_formats.AtUri] = None  #: Feed.


class DataDict(t.TypedDict):
    interactions: t.List['models.AppBskyFeedDefs.Interaction']  #: Interactions.
    feed: te.NotRequired[t.Optional[string_formats.AtUri]]  #: Feed.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`app.bsky.feed.sendInteractions`."""
