from atproto_client.models.record_registry import RECORD_TYPE_TO_MODEL_CLASS, register_record_types

__all__ = ['RECORD_TYPES', 'RECORD_TYPE_TO_MODEL_CLASS']
RECORD_TYPES = {
    'app.bsky.actor.contentVisibilityDeclaration': 'AppBskyActorContentVisibilityDeclaration',
    'app.bsky.actor.profile': 'AppBskyActorProfile',
    'app.bsky.actor.status': 'AppBskyActorStatus',
    'app.bsky.feed.generator': 'AppBskyFeedGenerator',
    'app.bsky.feed.like': 'AppBskyFeedLike',
    'app.bsky.feed.post': 'AppBskyFeedPost',
    'app.bsky.feed.postgate': 'AppBskyFeedPostgate',
    'app.bsky.feed.repost': 'AppBskyFeedRepost',
    'app.bsky.feed.threadgate': 'AppBskyFeedThreadgate',
    'app.bsky.graph.block': 'AppBskyGraphBlock',
    'app.bsky.graph.follow': 'AppBskyGraphFollow',
    'app.bsky.graph.list': 'AppBskyGraphList',
    'app.bsky.graph.listblock': 'AppBskyGraphListblock',
    'app.bsky.graph.listitem': 'AppBskyGraphListitem',
    'app.bsky.graph.referencelistoptout': 'AppBskyGraphReferencelistoptout',
    'app.bsky.graph.starterpack': 'AppBskyGraphStarterpack',
    'app.bsky.graph.verification': 'AppBskyGraphVerification',
    'app.bsky.labeler.service': 'AppBskyLabelerService',
    'app.bsky.notification.declaration': 'AppBskyNotificationDeclaration',
    'chat.bsky.actor.declaration': 'ChatBskyActorDeclaration',
    'com.atproto.lexicon.schema': 'ComAtprotoLexiconSchema',
    'com.germnetwork.declaration': 'ComGermnetworkDeclaration',
    'site.standard.document': 'SiteStandardDocument',
    'site.standard.graph.recommend': 'SiteStandardGraphRecommend',
    'site.standard.graph.subscription': 'SiteStandardGraphSubscription',
    'site.standard.publication': 'SiteStandardPublication',
    'site.standard.theme.basic': 'SiteStandardThemeBasic',
}
register_record_types('atproto_client.models', RECORD_TYPES)
