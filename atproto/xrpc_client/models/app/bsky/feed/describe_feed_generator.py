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


class Response(base.ResponseModelBase):

    """Output data model for :obj:`app.bsky.feed.describeFeedGenerator`."""

    did: str  #: Did.
    feeds: t.List['models.AppBskyFeedDescribeFeedGenerator.Feed']  #: Feeds.
    links: t.Optional['models.AppBskyFeedDescribeFeedGenerator.Links'] = None  #: Links.


class Feed(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.describeFeedGenerator`."""

    uri: str  #: Uri.

    py_type: te.Literal['app.bsky.feed.describeFeedGenerator#feed'] = Field(
        default='app.bsky.feed.describeFeedGenerator#feed', alias='$type'
    )


class Links(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.describeFeedGenerator`."""

    privacyPolicy: t.Optional[str] = None  #: Privacy policy.
    termsOfService: t.Optional[str] = None  #: Terms of service.

    py_type: te.Literal['app.bsky.feed.describeFeedGenerator#links'] = Field(
        default='app.bsky.feed.describeFeedGenerator#links', alias='$type'
    )
