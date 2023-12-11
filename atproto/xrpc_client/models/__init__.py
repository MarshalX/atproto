from atproto.xrpc_client.models.app.bsky.actor import defs as AppBskyActorDefs
from atproto.xrpc_client.models.app.bsky.actor import get_preferences as AppBskyActorGetPreferences
from atproto.xrpc_client.models.app.bsky.actor import get_profile as AppBskyActorGetProfile
from atproto.xrpc_client.models.app.bsky.actor import get_profiles as AppBskyActorGetProfiles
from atproto.xrpc_client.models.app.bsky.actor import get_suggestions as AppBskyActorGetSuggestions
from atproto.xrpc_client.models.app.bsky.actor import profile as AppBskyActorProfile
from atproto.xrpc_client.models.app.bsky.actor import put_preferences as AppBskyActorPutPreferences
from atproto.xrpc_client.models.app.bsky.actor import search_actors as AppBskyActorSearchActors
from atproto.xrpc_client.models.app.bsky.actor import search_actors_typeahead as AppBskyActorSearchActorsTypeahead
from atproto.xrpc_client.models.app.bsky.embed import external as AppBskyEmbedExternal
from atproto.xrpc_client.models.app.bsky.embed import images as AppBskyEmbedImages
from atproto.xrpc_client.models.app.bsky.embed import record as AppBskyEmbedRecord
from atproto.xrpc_client.models.app.bsky.embed import record_with_media as AppBskyEmbedRecordWithMedia
from atproto.xrpc_client.models.app.bsky.feed import defs as AppBskyFeedDefs
from atproto.xrpc_client.models.app.bsky.feed import describe_feed_generator as AppBskyFeedDescribeFeedGenerator
from atproto.xrpc_client.models.app.bsky.feed import generator as AppBskyFeedGenerator
from atproto.xrpc_client.models.app.bsky.feed import get_actor_feeds as AppBskyFeedGetActorFeeds
from atproto.xrpc_client.models.app.bsky.feed import get_actor_likes as AppBskyFeedGetActorLikes
from atproto.xrpc_client.models.app.bsky.feed import get_author_feed as AppBskyFeedGetAuthorFeed
from atproto.xrpc_client.models.app.bsky.feed import get_feed as AppBskyFeedGetFeed
from atproto.xrpc_client.models.app.bsky.feed import get_feed_generator as AppBskyFeedGetFeedGenerator
from atproto.xrpc_client.models.app.bsky.feed import get_feed_generators as AppBskyFeedGetFeedGenerators
from atproto.xrpc_client.models.app.bsky.feed import get_feed_skeleton as AppBskyFeedGetFeedSkeleton
from atproto.xrpc_client.models.app.bsky.feed import get_likes as AppBskyFeedGetLikes
from atproto.xrpc_client.models.app.bsky.feed import get_list_feed as AppBskyFeedGetListFeed
from atproto.xrpc_client.models.app.bsky.feed import get_post_thread as AppBskyFeedGetPostThread
from atproto.xrpc_client.models.app.bsky.feed import get_posts as AppBskyFeedGetPosts
from atproto.xrpc_client.models.app.bsky.feed import get_reposted_by as AppBskyFeedGetRepostedBy
from atproto.xrpc_client.models.app.bsky.feed import get_suggested_feeds as AppBskyFeedGetSuggestedFeeds
from atproto.xrpc_client.models.app.bsky.feed import get_timeline as AppBskyFeedGetTimeline
from atproto.xrpc_client.models.app.bsky.feed import like as AppBskyFeedLike
from atproto.xrpc_client.models.app.bsky.feed import post as AppBskyFeedPost
from atproto.xrpc_client.models.app.bsky.feed import repost as AppBskyFeedRepost
from atproto.xrpc_client.models.app.bsky.feed import search_posts as AppBskyFeedSearchPosts
from atproto.xrpc_client.models.app.bsky.feed import threadgate as AppBskyFeedThreadgate
from atproto.xrpc_client.models.app.bsky.graph import block as AppBskyGraphBlock
from atproto.xrpc_client.models.app.bsky.graph import defs as AppBskyGraphDefs
from atproto.xrpc_client.models.app.bsky.graph import follow as AppBskyGraphFollow
from atproto.xrpc_client.models.app.bsky.graph import get_blocks as AppBskyGraphGetBlocks
from atproto.xrpc_client.models.app.bsky.graph import get_followers as AppBskyGraphGetFollowers
from atproto.xrpc_client.models.app.bsky.graph import get_follows as AppBskyGraphGetFollows
from atproto.xrpc_client.models.app.bsky.graph import get_list as AppBskyGraphGetList
from atproto.xrpc_client.models.app.bsky.graph import get_list_blocks as AppBskyGraphGetListBlocks
from atproto.xrpc_client.models.app.bsky.graph import get_list_mutes as AppBskyGraphGetListMutes
from atproto.xrpc_client.models.app.bsky.graph import get_lists as AppBskyGraphGetLists
from atproto.xrpc_client.models.app.bsky.graph import get_mutes as AppBskyGraphGetMutes
from atproto.xrpc_client.models.app.bsky.graph import (
    get_suggested_follows_by_actor as AppBskyGraphGetSuggestedFollowsByActor,
)
from atproto.xrpc_client.models.app.bsky.graph import list as AppBskyGraphList
from atproto.xrpc_client.models.app.bsky.graph import listblock as AppBskyGraphListblock
from atproto.xrpc_client.models.app.bsky.graph import listitem as AppBskyGraphListitem
from atproto.xrpc_client.models.app.bsky.graph import mute_actor as AppBskyGraphMuteActor
from atproto.xrpc_client.models.app.bsky.graph import mute_actor_list as AppBskyGraphMuteActorList
from atproto.xrpc_client.models.app.bsky.graph import unmute_actor as AppBskyGraphUnmuteActor
from atproto.xrpc_client.models.app.bsky.graph import unmute_actor_list as AppBskyGraphUnmuteActorList
from atproto.xrpc_client.models.app.bsky.notification import get_unread_count as AppBskyNotificationGetUnreadCount
from atproto.xrpc_client.models.app.bsky.notification import list_notifications as AppBskyNotificationListNotifications
from atproto.xrpc_client.models.app.bsky.notification import register_push as AppBskyNotificationRegisterPush
from atproto.xrpc_client.models.app.bsky.notification import update_seen as AppBskyNotificationUpdateSeen
from atproto.xrpc_client.models.app.bsky.richtext import facet as AppBskyRichtextFacet
from atproto.xrpc_client.models.app.bsky.unspecced import defs as AppBskyUnspeccedDefs
from atproto.xrpc_client.models.app.bsky.unspecced import get_popular as AppBskyUnspeccedGetPopular
from atproto.xrpc_client.models.app.bsky.unspecced import (
    get_popular_feed_generators as AppBskyUnspeccedGetPopularFeedGenerators,
)
from atproto.xrpc_client.models.app.bsky.unspecced import get_timeline_skeleton as AppBskyUnspeccedGetTimelineSkeleton
from atproto.xrpc_client.models.app.bsky.unspecced import search_actors_skeleton as AppBskyUnspeccedSearchActorsSkeleton
from atproto.xrpc_client.models.app.bsky.unspecced import search_posts_skeleton as AppBskyUnspeccedSearchPostsSkeleton
from atproto.xrpc_client.models.com.atproto.admin import defs as ComAtprotoAdminDefs
from atproto.xrpc_client.models.com.atproto.admin import delete_account as ComAtprotoAdminDeleteAccount
from atproto.xrpc_client.models.com.atproto.admin import disable_account_invites as ComAtprotoAdminDisableAccountInvites
from atproto.xrpc_client.models.com.atproto.admin import disable_invite_codes as ComAtprotoAdminDisableInviteCodes
from atproto.xrpc_client.models.com.atproto.admin import emit_moderation_event as ComAtprotoAdminEmitModerationEvent
from atproto.xrpc_client.models.com.atproto.admin import enable_account_invites as ComAtprotoAdminEnableAccountInvites
from atproto.xrpc_client.models.com.atproto.admin import get_account_info as ComAtprotoAdminGetAccountInfo
from atproto.xrpc_client.models.com.atproto.admin import get_invite_codes as ComAtprotoAdminGetInviteCodes
from atproto.xrpc_client.models.com.atproto.admin import get_moderation_event as ComAtprotoAdminGetModerationEvent
from atproto.xrpc_client.models.com.atproto.admin import get_record as ComAtprotoAdminGetRecord
from atproto.xrpc_client.models.com.atproto.admin import get_repo as ComAtprotoAdminGetRepo
from atproto.xrpc_client.models.com.atproto.admin import get_subject_status as ComAtprotoAdminGetSubjectStatus
from atproto.xrpc_client.models.com.atproto.admin import query_moderation_events as ComAtprotoAdminQueryModerationEvents
from atproto.xrpc_client.models.com.atproto.admin import (
    query_moderation_statuses as ComAtprotoAdminQueryModerationStatuses,
)
from atproto.xrpc_client.models.com.atproto.admin import search_repos as ComAtprotoAdminSearchRepos
from atproto.xrpc_client.models.com.atproto.admin import send_email as ComAtprotoAdminSendEmail
from atproto.xrpc_client.models.com.atproto.admin import update_account_email as ComAtprotoAdminUpdateAccountEmail
from atproto.xrpc_client.models.com.atproto.admin import update_account_handle as ComAtprotoAdminUpdateAccountHandle
from atproto.xrpc_client.models.com.atproto.admin import update_subject_status as ComAtprotoAdminUpdateSubjectStatus
from atproto.xrpc_client.models.com.atproto.identity import resolve_handle as ComAtprotoIdentityResolveHandle
from atproto.xrpc_client.models.com.atproto.identity import update_handle as ComAtprotoIdentityUpdateHandle
from atproto.xrpc_client.models.com.atproto.label import defs as ComAtprotoLabelDefs
from atproto.xrpc_client.models.com.atproto.label import query_labels as ComAtprotoLabelQueryLabels
from atproto.xrpc_client.models.com.atproto.label import subscribe_labels as ComAtprotoLabelSubscribeLabels
from atproto.xrpc_client.models.com.atproto.moderation import create_report as ComAtprotoModerationCreateReport
from atproto.xrpc_client.models.com.atproto.moderation import defs as ComAtprotoModerationDefs
from atproto.xrpc_client.models.com.atproto.repo import apply_writes as ComAtprotoRepoApplyWrites
from atproto.xrpc_client.models.com.atproto.repo import create_record as ComAtprotoRepoCreateRecord
from atproto.xrpc_client.models.com.atproto.repo import delete_record as ComAtprotoRepoDeleteRecord
from atproto.xrpc_client.models.com.atproto.repo import describe_repo as ComAtprotoRepoDescribeRepo
from atproto.xrpc_client.models.com.atproto.repo import get_record as ComAtprotoRepoGetRecord
from atproto.xrpc_client.models.com.atproto.repo import list_records as ComAtprotoRepoListRecords
from atproto.xrpc_client.models.com.atproto.repo import put_record as ComAtprotoRepoPutRecord
from atproto.xrpc_client.models.com.atproto.repo import strong_ref as ComAtprotoRepoStrongRef
from atproto.xrpc_client.models.com.atproto.repo import upload_blob as ComAtprotoRepoUploadBlob
from atproto.xrpc_client.models.com.atproto.server import confirm_email as ComAtprotoServerConfirmEmail
from atproto.xrpc_client.models.com.atproto.server import create_account as ComAtprotoServerCreateAccount
from atproto.xrpc_client.models.com.atproto.server import create_app_password as ComAtprotoServerCreateAppPassword
from atproto.xrpc_client.models.com.atproto.server import create_invite_code as ComAtprotoServerCreateInviteCode
from atproto.xrpc_client.models.com.atproto.server import create_invite_codes as ComAtprotoServerCreateInviteCodes
from atproto.xrpc_client.models.com.atproto.server import create_session as ComAtprotoServerCreateSession
from atproto.xrpc_client.models.com.atproto.server import defs as ComAtprotoServerDefs
from atproto.xrpc_client.models.com.atproto.server import delete_account as ComAtprotoServerDeleteAccount
from atproto.xrpc_client.models.com.atproto.server import delete_session as ComAtprotoServerDeleteSession
from atproto.xrpc_client.models.com.atproto.server import describe_server as ComAtprotoServerDescribeServer
from atproto.xrpc_client.models.com.atproto.server import (
    get_account_invite_codes as ComAtprotoServerGetAccountInviteCodes,
)
from atproto.xrpc_client.models.com.atproto.server import get_session as ComAtprotoServerGetSession
from atproto.xrpc_client.models.com.atproto.server import list_app_passwords as ComAtprotoServerListAppPasswords
from atproto.xrpc_client.models.com.atproto.server import refresh_session as ComAtprotoServerRefreshSession
from atproto.xrpc_client.models.com.atproto.server import request_account_delete as ComAtprotoServerRequestAccountDelete
from atproto.xrpc_client.models.com.atproto.server import (
    request_email_confirmation as ComAtprotoServerRequestEmailConfirmation,
)
from atproto.xrpc_client.models.com.atproto.server import request_email_update as ComAtprotoServerRequestEmailUpdate
from atproto.xrpc_client.models.com.atproto.server import request_password_reset as ComAtprotoServerRequestPasswordReset
from atproto.xrpc_client.models.com.atproto.server import reserve_signing_key as ComAtprotoServerReserveSigningKey
from atproto.xrpc_client.models.com.atproto.server import reset_password as ComAtprotoServerResetPassword
from atproto.xrpc_client.models.com.atproto.server import revoke_app_password as ComAtprotoServerRevokeAppPassword
from atproto.xrpc_client.models.com.atproto.server import update_email as ComAtprotoServerUpdateEmail
from atproto.xrpc_client.models.com.atproto.sync import get_blob as ComAtprotoSyncGetBlob
from atproto.xrpc_client.models.com.atproto.sync import get_blocks as ComAtprotoSyncGetBlocks
from atproto.xrpc_client.models.com.atproto.sync import get_checkout as ComAtprotoSyncGetCheckout
from atproto.xrpc_client.models.com.atproto.sync import get_head as ComAtprotoSyncGetHead
from atproto.xrpc_client.models.com.atproto.sync import get_latest_commit as ComAtprotoSyncGetLatestCommit
from atproto.xrpc_client.models.com.atproto.sync import get_record as ComAtprotoSyncGetRecord
from atproto.xrpc_client.models.com.atproto.sync import get_repo as ComAtprotoSyncGetRepo
from atproto.xrpc_client.models.com.atproto.sync import list_blobs as ComAtprotoSyncListBlobs
from atproto.xrpc_client.models.com.atproto.sync import list_repos as ComAtprotoSyncListRepos
from atproto.xrpc_client.models.com.atproto.sync import notify_of_update as ComAtprotoSyncNotifyOfUpdate
from atproto.xrpc_client.models.com.atproto.sync import request_crawl as ComAtprotoSyncRequestCrawl
from atproto.xrpc_client.models.com.atproto.sync import subscribe_repos as ComAtprotoSyncSubscribeRepos
from atproto.xrpc_client.models.com.atproto.temp import fetch_labels as ComAtprotoTempFetchLabels
from atproto.xrpc_client.models.com.atproto.temp import import_repo as ComAtprotoTempImportRepo
from atproto.xrpc_client.models.com.atproto.temp import push_blob as ComAtprotoTempPushBlob
from atproto.xrpc_client.models.com.atproto.temp import transfer_account as ComAtprotoTempTransferAccount
from atproto.xrpc_client.models.models_loader import load_models
from atproto.xrpc_client.models.utils import (
    create_strong_ref,
    get_model_as_dict,
    get_model_as_json,
    get_or_create,
    is_record_type,
)


class _Ids:
    AppBskyActorDefs: str = 'app.bsky.actor.defs'
    AppBskyActorGetPreferences: str = 'app.bsky.actor.getPreferences'
    AppBskyActorGetProfile: str = 'app.bsky.actor.getProfile'
    AppBskyActorGetProfiles: str = 'app.bsky.actor.getProfiles'
    AppBskyActorGetSuggestions: str = 'app.bsky.actor.getSuggestions'
    AppBskyActorProfile: str = 'app.bsky.actor.profile'
    AppBskyActorPutPreferences: str = 'app.bsky.actor.putPreferences'
    AppBskyActorSearchActors: str = 'app.bsky.actor.searchActors'
    AppBskyActorSearchActorsTypeahead: str = 'app.bsky.actor.searchActorsTypeahead'
    AppBskyEmbedExternal: str = 'app.bsky.embed.external'
    AppBskyEmbedImages: str = 'app.bsky.embed.images'
    AppBskyEmbedRecord: str = 'app.bsky.embed.record'
    AppBskyEmbedRecordWithMedia: str = 'app.bsky.embed.recordWithMedia'
    AppBskyFeedDefs: str = 'app.bsky.feed.defs'
    AppBskyFeedDescribeFeedGenerator: str = 'app.bsky.feed.describeFeedGenerator'
    AppBskyFeedGenerator: str = 'app.bsky.feed.generator'
    AppBskyFeedGetActorFeeds: str = 'app.bsky.feed.getActorFeeds'
    AppBskyFeedGetActorLikes: str = 'app.bsky.feed.getActorLikes'
    AppBskyFeedGetAuthorFeed: str = 'app.bsky.feed.getAuthorFeed'
    AppBskyFeedGetFeed: str = 'app.bsky.feed.getFeed'
    AppBskyFeedGetFeedGenerator: str = 'app.bsky.feed.getFeedGenerator'
    AppBskyFeedGetFeedGenerators: str = 'app.bsky.feed.getFeedGenerators'
    AppBskyFeedGetFeedSkeleton: str = 'app.bsky.feed.getFeedSkeleton'
    AppBskyFeedGetLikes: str = 'app.bsky.feed.getLikes'
    AppBskyFeedGetListFeed: str = 'app.bsky.feed.getListFeed'
    AppBskyFeedGetPostThread: str = 'app.bsky.feed.getPostThread'
    AppBskyFeedGetPosts: str = 'app.bsky.feed.getPosts'
    AppBskyFeedGetRepostedBy: str = 'app.bsky.feed.getRepostedBy'
    AppBskyFeedGetSuggestedFeeds: str = 'app.bsky.feed.getSuggestedFeeds'
    AppBskyFeedGetTimeline: str = 'app.bsky.feed.getTimeline'
    AppBskyFeedLike: str = 'app.bsky.feed.like'
    AppBskyFeedPost: str = 'app.bsky.feed.post'
    AppBskyFeedRepost: str = 'app.bsky.feed.repost'
    AppBskyFeedSearchPosts: str = 'app.bsky.feed.searchPosts'
    AppBskyFeedThreadgate: str = 'app.bsky.feed.threadgate'
    AppBskyGraphBlock: str = 'app.bsky.graph.block'
    AppBskyGraphDefs: str = 'app.bsky.graph.defs'
    AppBskyGraphFollow: str = 'app.bsky.graph.follow'
    AppBskyGraphGetBlocks: str = 'app.bsky.graph.getBlocks'
    AppBskyGraphGetFollowers: str = 'app.bsky.graph.getFollowers'
    AppBskyGraphGetFollows: str = 'app.bsky.graph.getFollows'
    AppBskyGraphGetList: str = 'app.bsky.graph.getList'
    AppBskyGraphGetListBlocks: str = 'app.bsky.graph.getListBlocks'
    AppBskyGraphGetListMutes: str = 'app.bsky.graph.getListMutes'
    AppBskyGraphGetLists: str = 'app.bsky.graph.getLists'
    AppBskyGraphGetMutes: str = 'app.bsky.graph.getMutes'
    AppBskyGraphGetSuggestedFollowsByActor: str = 'app.bsky.graph.getSuggestedFollowsByActor'
    AppBskyGraphList: str = 'app.bsky.graph.list'
    AppBskyGraphListblock: str = 'app.bsky.graph.listblock'
    AppBskyGraphListitem: str = 'app.bsky.graph.listitem'
    AppBskyGraphMuteActor: str = 'app.bsky.graph.muteActor'
    AppBskyGraphMuteActorList: str = 'app.bsky.graph.muteActorList'
    AppBskyGraphUnmuteActor: str = 'app.bsky.graph.unmuteActor'
    AppBskyGraphUnmuteActorList: str = 'app.bsky.graph.unmuteActorList'
    AppBskyNotificationGetUnreadCount: str = 'app.bsky.notification.getUnreadCount'
    AppBskyNotificationListNotifications: str = 'app.bsky.notification.listNotifications'
    AppBskyNotificationRegisterPush: str = 'app.bsky.notification.registerPush'
    AppBskyNotificationUpdateSeen: str = 'app.bsky.notification.updateSeen'
    AppBskyRichtextFacet: str = 'app.bsky.richtext.facet'
    AppBskyUnspeccedDefs: str = 'app.bsky.unspecced.defs'
    AppBskyUnspeccedGetPopular: str = 'app.bsky.unspecced.getPopular'
    AppBskyUnspeccedGetPopularFeedGenerators: str = 'app.bsky.unspecced.getPopularFeedGenerators'
    AppBskyUnspeccedGetTimelineSkeleton: str = 'app.bsky.unspecced.getTimelineSkeleton'
    AppBskyUnspeccedSearchActorsSkeleton: str = 'app.bsky.unspecced.searchActorsSkeleton'
    AppBskyUnspeccedSearchPostsSkeleton: str = 'app.bsky.unspecced.searchPostsSkeleton'
    ComAtprotoAdminDefs: str = 'com.atproto.admin.defs'
    ComAtprotoAdminDeleteAccount: str = 'com.atproto.admin.deleteAccount'
    ComAtprotoAdminDisableAccountInvites: str = 'com.atproto.admin.disableAccountInvites'
    ComAtprotoAdminDisableInviteCodes: str = 'com.atproto.admin.disableInviteCodes'
    ComAtprotoAdminEmitModerationEvent: str = 'com.atproto.admin.emitModerationEvent'
    ComAtprotoAdminEnableAccountInvites: str = 'com.atproto.admin.enableAccountInvites'
    ComAtprotoAdminGetAccountInfo: str = 'com.atproto.admin.getAccountInfo'
    ComAtprotoAdminGetInviteCodes: str = 'com.atproto.admin.getInviteCodes'
    ComAtprotoAdminGetModerationEvent: str = 'com.atproto.admin.getModerationEvent'
    ComAtprotoAdminGetRecord: str = 'com.atproto.admin.getRecord'
    ComAtprotoAdminGetRepo: str = 'com.atproto.admin.getRepo'
    ComAtprotoAdminGetSubjectStatus: str = 'com.atproto.admin.getSubjectStatus'
    ComAtprotoAdminQueryModerationEvents: str = 'com.atproto.admin.queryModerationEvents'
    ComAtprotoAdminQueryModerationStatuses: str = 'com.atproto.admin.queryModerationStatuses'
    ComAtprotoAdminSearchRepos: str = 'com.atproto.admin.searchRepos'
    ComAtprotoAdminSendEmail: str = 'com.atproto.admin.sendEmail'
    ComAtprotoAdminUpdateAccountEmail: str = 'com.atproto.admin.updateAccountEmail'
    ComAtprotoAdminUpdateAccountHandle: str = 'com.atproto.admin.updateAccountHandle'
    ComAtprotoAdminUpdateSubjectStatus: str = 'com.atproto.admin.updateSubjectStatus'
    ComAtprotoIdentityResolveHandle: str = 'com.atproto.identity.resolveHandle'
    ComAtprotoIdentityUpdateHandle: str = 'com.atproto.identity.updateHandle'
    ComAtprotoLabelDefs: str = 'com.atproto.label.defs'
    ComAtprotoLabelQueryLabels: str = 'com.atproto.label.queryLabels'
    ComAtprotoLabelSubscribeLabels: str = 'com.atproto.label.subscribeLabels'
    ComAtprotoModerationCreateReport: str = 'com.atproto.moderation.createReport'
    ComAtprotoModerationDefs: str = 'com.atproto.moderation.defs'
    ComAtprotoRepoApplyWrites: str = 'com.atproto.repo.applyWrites'
    ComAtprotoRepoCreateRecord: str = 'com.atproto.repo.createRecord'
    ComAtprotoRepoDeleteRecord: str = 'com.atproto.repo.deleteRecord'
    ComAtprotoRepoDescribeRepo: str = 'com.atproto.repo.describeRepo'
    ComAtprotoRepoGetRecord: str = 'com.atproto.repo.getRecord'
    ComAtprotoRepoListRecords: str = 'com.atproto.repo.listRecords'
    ComAtprotoRepoPutRecord: str = 'com.atproto.repo.putRecord'
    ComAtprotoRepoStrongRef: str = 'com.atproto.repo.strongRef'
    ComAtprotoRepoUploadBlob: str = 'com.atproto.repo.uploadBlob'
    ComAtprotoServerConfirmEmail: str = 'com.atproto.server.confirmEmail'
    ComAtprotoServerCreateAccount: str = 'com.atproto.server.createAccount'
    ComAtprotoServerCreateAppPassword: str = 'com.atproto.server.createAppPassword'
    ComAtprotoServerCreateInviteCode: str = 'com.atproto.server.createInviteCode'
    ComAtprotoServerCreateInviteCodes: str = 'com.atproto.server.createInviteCodes'
    ComAtprotoServerCreateSession: str = 'com.atproto.server.createSession'
    ComAtprotoServerDefs: str = 'com.atproto.server.defs'
    ComAtprotoServerDeleteAccount: str = 'com.atproto.server.deleteAccount'
    ComAtprotoServerDeleteSession: str = 'com.atproto.server.deleteSession'
    ComAtprotoServerDescribeServer: str = 'com.atproto.server.describeServer'
    ComAtprotoServerGetAccountInviteCodes: str = 'com.atproto.server.getAccountInviteCodes'
    ComAtprotoServerGetSession: str = 'com.atproto.server.getSession'
    ComAtprotoServerListAppPasswords: str = 'com.atproto.server.listAppPasswords'
    ComAtprotoServerRefreshSession: str = 'com.atproto.server.refreshSession'
    ComAtprotoServerRequestAccountDelete: str = 'com.atproto.server.requestAccountDelete'
    ComAtprotoServerRequestEmailConfirmation: str = 'com.atproto.server.requestEmailConfirmation'
    ComAtprotoServerRequestEmailUpdate: str = 'com.atproto.server.requestEmailUpdate'
    ComAtprotoServerRequestPasswordReset: str = 'com.atproto.server.requestPasswordReset'
    ComAtprotoServerReserveSigningKey: str = 'com.atproto.server.reserveSigningKey'
    ComAtprotoServerResetPassword: str = 'com.atproto.server.resetPassword'
    ComAtprotoServerRevokeAppPassword: str = 'com.atproto.server.revokeAppPassword'
    ComAtprotoServerUpdateEmail: str = 'com.atproto.server.updateEmail'
    ComAtprotoSyncGetBlob: str = 'com.atproto.sync.getBlob'
    ComAtprotoSyncGetBlocks: str = 'com.atproto.sync.getBlocks'
    ComAtprotoSyncGetCheckout: str = 'com.atproto.sync.getCheckout'
    ComAtprotoSyncGetHead: str = 'com.atproto.sync.getHead'
    ComAtprotoSyncGetLatestCommit: str = 'com.atproto.sync.getLatestCommit'
    ComAtprotoSyncGetRecord: str = 'com.atproto.sync.getRecord'
    ComAtprotoSyncGetRepo: str = 'com.atproto.sync.getRepo'
    ComAtprotoSyncListBlobs: str = 'com.atproto.sync.listBlobs'
    ComAtprotoSyncListRepos: str = 'com.atproto.sync.listRepos'
    ComAtprotoSyncNotifyOfUpdate: str = 'com.atproto.sync.notifyOfUpdate'
    ComAtprotoSyncRequestCrawl: str = 'com.atproto.sync.requestCrawl'
    ComAtprotoSyncSubscribeRepos: str = 'com.atproto.sync.subscribeRepos'
    ComAtprotoTempFetchLabels: str = 'com.atproto.temp.fetchLabels'
    ComAtprotoTempImportRepo: str = 'com.atproto.temp.importRepo'
    ComAtprotoTempPushBlob: str = 'com.atproto.temp.pushBlob'
    ComAtprotoTempTransferAccount: str = 'com.atproto.temp.transferAccount'


ids = _Ids()
load_models()
