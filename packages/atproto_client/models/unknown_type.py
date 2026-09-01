import typing as t

import typing_extensions as te

from atproto_client.models import unknown_union

if t.TYPE_CHECKING:
    from atproto_client import models
    from atproto_client.models import dot_dict

UnknownRecordType: te.TypeAlias = t.Union[
    'models.AppBskyActorContentVisibilityDeclaration.Record',
    'models.AppBskyActorProfile.Record',
    'models.AppBskyActorStatus.Record',
    'models.AppBskyFeedGenerator.Record',
    'models.AppBskyFeedLike.Record',
    'models.AppBskyFeedPost.Record',
    'models.AppBskyFeedPostgate.Record',
    'models.AppBskyFeedRepost.Record',
    'models.AppBskyFeedThreadgate.Record',
    'models.AppBskyGraphBlock.Record',
    'models.AppBskyGraphFollow.Record',
    'models.AppBskyGraphList.Record',
    'models.AppBskyGraphListblock.Record',
    'models.AppBskyGraphListitem.Record',
    'models.AppBskyGraphReferencelistoptout.Record',
    'models.AppBskyGraphStarterpack.Record',
    'models.AppBskyGraphVerification.Record',
    'models.AppBskyLabelerService.Record',
    'models.AppBskyNotificationDeclaration.Record',
    'models.ChatBskyActorDeclaration.Record',
    'models.ComAtprotoLexiconSchema.Record',
    'models.ComGermnetworkDeclaration.Record',
    'models.SiteStandardDocument.Record',
    'models.SiteStandardGraphRecommend.Record',
    'models.SiteStandardGraphSubscription.Record',
    'models.SiteStandardPublication.Record',
    'models.SiteStandardThemeBasic.Record',
]
if t.TYPE_CHECKING:
    UnknownType: te.TypeAlias = te.Annotated[
        t.Union[UnknownRecordType, 'dot_dict.DotDictType'], unknown_union.UnknownRecordFallback
    ]
    UnknownInputType: te.TypeAlias = t.Union[UnknownType, t.Dict[str, t.Any]]
else:
    UnknownType = te.Annotated[t.Any, unknown_union.UnknownRecordFallback]
    UnknownInputType = UnknownType
