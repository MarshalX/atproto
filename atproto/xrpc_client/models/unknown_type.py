import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto.xrpc_client import models
    from atproto.xrpc_client.models import dot_dict

UnknownRecordType: te.TypeAlias = t.Union[
    'models.AppBskyFeedGenerator.Main',
    'models.AppBskyActorProfile.Main',
    'models.AppBskyFeedRepost.Main',
    'models.AppBskyGraphListitem.Main',
    'models.AppBskyFeedLike.Main',
    'models.AppBskyGraphFollow.Main',
    'models.AppBskyGraphList.Main',
    'models.AppBskyGraphListblock.Main',
    'models.AppBskyGraphBlock.Main',
    'models.AppBskyFeedPost.Main',
]
UnknownRecordTypePydantic = te.Annotated[
    t.Union[
        'models.AppBskyFeedGenerator.Main',
        'models.AppBskyActorProfile.Main',
        'models.AppBskyFeedRepost.Main',
        'models.AppBskyGraphListitem.Main',
        'models.AppBskyFeedLike.Main',
        'models.AppBskyGraphFollow.Main',
        'models.AppBskyGraphList.Main',
        'models.AppBskyGraphListblock.Main',
        'models.AppBskyGraphBlock.Main',
        'models.AppBskyFeedPost.Main',
    ],
    Field(discriminator='py_type'),
]
UnknownType: te.TypeAlias = t.Union[UnknownRecordTypePydantic, 'dot_dict.DotDictType']
