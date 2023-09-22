from atproto.xrpc_client import models

RECORD_TYPE_TO_MODEL_CLASS = {
    'app.bsky.actor.profile': models.AppBskyActorProfile.Main,
    'app.bsky.feed.generator': models.AppBskyFeedGenerator.Main,
    'app.bsky.feed.like': models.AppBskyFeedLike.Main,
    'app.bsky.feed.post': models.AppBskyFeedPost.Main,
    'app.bsky.feed.repost': models.AppBskyFeedRepost.Main,
    'app.bsky.feed.threadgate': models.AppBskyFeedThreadgate.Main,
    'app.bsky.graph.block': models.AppBskyGraphBlock.Main,
    'app.bsky.graph.follow': models.AppBskyGraphFollow.Main,
    'app.bsky.graph.list': models.AppBskyGraphList.Main,
    'app.bsky.graph.listblock': models.AppBskyGraphListblock.Main,
    'app.bsky.graph.listitem': models.AppBskyGraphListitem.Main,
}
