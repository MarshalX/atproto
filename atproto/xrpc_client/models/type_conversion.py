from atproto.xrpc_client import models

RECORD_TYPE_TO_MODEL_CLASS = {
    'app.bsky.actor.profile': models.AppBskyActorProfile.Main,
    'app.bsky.feed.repost': models.AppBskyFeedRepost.Main,
    'app.bsky.feed.like': models.AppBskyFeedLike.Main,
    'app.bsky.graph.follow': models.AppBskyGraphFollow.Main,
    'app.bsky.graph.block': models.AppBskyGraphBlock.Main,
    'app.bsky.feed.post': models.AppBskyFeedPost.Main,
}
