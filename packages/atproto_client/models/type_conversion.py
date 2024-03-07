from atproto_client import models

RECORD_TYPE_TO_MODEL_CLASS = {
    'app.bsky.actor.profile': models.AppBskyActorProfile.Record,
    'app.bsky.feed.generator': models.AppBskyFeedGenerator.Record,
    'app.bsky.feed.like': models.AppBskyFeedLike.Record,
    'app.bsky.feed.post': models.AppBskyFeedPost.Record,
    'app.bsky.feed.repost': models.AppBskyFeedRepost.Record,
    'app.bsky.feed.threadgate': models.AppBskyFeedThreadgate.Record,
    'app.bsky.graph.block': models.AppBskyGraphBlock.Record,
    'app.bsky.graph.follow': models.AppBskyGraphFollow.Record,
    'app.bsky.graph.list': models.AppBskyGraphList.Record,
    'app.bsky.graph.listblock': models.AppBskyGraphListblock.Record,
    'app.bsky.graph.listitem': models.AppBskyGraphListitem.Record,
    'app.bsky.labeler.service': models.AppBskyLabelerService.Record,
}
