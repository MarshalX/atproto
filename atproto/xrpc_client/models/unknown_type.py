import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto.xrpc_client import models
    from atproto.xrpc_client.models import dot_dict

UnknownRecordType: te.TypeAlias = t.Union[
    'models.AppBskyActorProfile.Main',
    'models.AppBskyFeedGenerator.Main',
    'models.AppBskyFeedLike.Main',
    'models.AppBskyFeedPost.Main',
    'models.AppBskyFeedRepost.Main',
    'models.AppBskyFeedThreadgate.Main',
    'models.AppBskyGraphBlock.Main',
    'models.AppBskyGraphFollow.Main',
    'models.AppBskyGraphList.Main',
    'models.AppBskyGraphListblock.Main',
    'models.AppBskyGraphListitem.Main',
]
UnknownRecordTypePydantic = te.Annotated[
    t.Union[
        'models.AppBskyActorProfile.Main',
        'models.AppBskyFeedGenerator.Main',
        'models.AppBskyFeedLike.Main',
        'models.AppBskyFeedPost.Main',
        'models.AppBskyFeedRepost.Main',
        'models.AppBskyFeedThreadgate.Main',
        'models.AppBskyGraphBlock.Main',
        'models.AppBskyGraphFollow.Main',
        'models.AppBskyGraphList.Main',
        'models.AppBskyGraphListblock.Main',
        'models.AppBskyGraphListitem.Main',
    ],
    Field(discriminator='py_type'),
]
UnknownType: te.TypeAlias = t.Union[UnknownRecordTypePydantic, 'dot_dict.DotDictType']
UnknownInputType: te.TypeAlias = t.Union[UnknownType, t.Dict[str, t.Any]]
