##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t
from dataclasses import dataclass

from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


@dataclass
class Response(base.ResponseModelBase):

    """Output data model for :obj:`app.bsky.feed.describeFeedGenerator`."""

    did: str  #: Did.
    feeds: t.List['models.AppBskyFeedDescribeFeedGenerator.Feed']  #: Feeds.
    links: t.Optional['models.AppBskyFeedDescribeFeedGenerator.Links'] = None  #: Links.


@dataclass
class Feed(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.describeFeedGenerator`."""

    uri: str  #: Uri.

    _type: str = 'app.bsky.feed.describeFeedGenerator#feed'


@dataclass
class Links(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.describeFeedGenerator`."""

    privacyPolicy: t.Optional[str] = None  #: Privacy policy.
    termsOfService: t.Optional[str] = None  #: Terms of service.

    _type: str = 'app.bsky.feed.describeFeedGenerator#links'
