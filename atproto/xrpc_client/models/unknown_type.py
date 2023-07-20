import typing as t

import typing_extensions as te

if t.TYPE_CHECKING:
    from atproto.xrpc_client import models

UnknownRecordType: te.TypeAlias = t.Union[
    'models.AppBskyFeedGenerator.Main',
    'models.AppBskyActorProfile.Main',
    'models.AppBskyFeedRepost.Main',
    'models.AppBskyGraphListitem.Main',
    'models.AppBskyFeedLike.Main',
    'models.AppBskyGraphFollow.Main',
    'models.AppBskyGraphList.Main',
    'models.AppBskyGraphBlock.Main',
    'models.AppBskyFeedPost.Main',
]
