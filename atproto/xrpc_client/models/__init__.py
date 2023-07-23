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
from atproto.xrpc_client.models.app.bsky.feed import get_author_feed as AppBskyFeedGetAuthorFeed
from atproto.xrpc_client.models.app.bsky.feed import get_feed as AppBskyFeedGetFeed
from atproto.xrpc_client.models.app.bsky.feed import get_feed_generator as AppBskyFeedGetFeedGenerator
from atproto.xrpc_client.models.app.bsky.feed import get_feed_generators as AppBskyFeedGetFeedGenerators
from atproto.xrpc_client.models.app.bsky.feed import get_feed_skeleton as AppBskyFeedGetFeedSkeleton
from atproto.xrpc_client.models.app.bsky.feed import get_likes as AppBskyFeedGetLikes
from atproto.xrpc_client.models.app.bsky.feed import get_post_thread as AppBskyFeedGetPostThread
from atproto.xrpc_client.models.app.bsky.feed import get_posts as AppBskyFeedGetPosts
from atproto.xrpc_client.models.app.bsky.feed import get_reposted_by as AppBskyFeedGetRepostedBy
from atproto.xrpc_client.models.app.bsky.feed import get_timeline as AppBskyFeedGetTimeline
from atproto.xrpc_client.models.app.bsky.feed import like as AppBskyFeedLike
from atproto.xrpc_client.models.app.bsky.feed import post as AppBskyFeedPost
from atproto.xrpc_client.models.app.bsky.feed import repost as AppBskyFeedRepost
from atproto.xrpc_client.models.app.bsky.graph import block as AppBskyGraphBlock
from atproto.xrpc_client.models.app.bsky.graph import defs as AppBskyGraphDefs
from atproto.xrpc_client.models.app.bsky.graph import follow as AppBskyGraphFollow
from atproto.xrpc_client.models.app.bsky.graph import get_blocks as AppBskyGraphGetBlocks
from atproto.xrpc_client.models.app.bsky.graph import get_followers as AppBskyGraphGetFollowers
from atproto.xrpc_client.models.app.bsky.graph import get_follows as AppBskyGraphGetFollows
from atproto.xrpc_client.models.app.bsky.graph import get_list as AppBskyGraphGetList
from atproto.xrpc_client.models.app.bsky.graph import get_list_mutes as AppBskyGraphGetListMutes
from atproto.xrpc_client.models.app.bsky.graph import get_lists as AppBskyGraphGetLists
from atproto.xrpc_client.models.app.bsky.graph import get_mutes as AppBskyGraphGetMutes
from atproto.xrpc_client.models.app.bsky.graph import list as AppBskyGraphList
from atproto.xrpc_client.models.app.bsky.graph import listitem as AppBskyGraphListitem
from atproto.xrpc_client.models.app.bsky.graph import mute_actor as AppBskyGraphMuteActor
from atproto.xrpc_client.models.app.bsky.graph import mute_actor_list as AppBskyGraphMuteActorList
from atproto.xrpc_client.models.app.bsky.graph import unmute_actor as AppBskyGraphUnmuteActor
from atproto.xrpc_client.models.app.bsky.graph import unmute_actor_list as AppBskyGraphUnmuteActorList
from atproto.xrpc_client.models.app.bsky.notification import get_unread_count as AppBskyNotificationGetUnreadCount
from atproto.xrpc_client.models.app.bsky.notification import list_notifications as AppBskyNotificationListNotifications
from atproto.xrpc_client.models.app.bsky.notification import update_seen as AppBskyNotificationUpdateSeen
from atproto.xrpc_client.models.app.bsky.richtext import facet as AppBskyRichtextFacet
from atproto.xrpc_client.models.app.bsky.unspecced import get_popular as AppBskyUnspeccedGetPopular
from atproto.xrpc_client.models.app.bsky.unspecced import (
    get_popular_feed_generators as AppBskyUnspeccedGetPopularFeedGenerators,
)
from atproto.xrpc_client.models.app.bsky.unspecced import get_timeline_skeleton as AppBskyUnspeccedGetTimelineSkeleton
from atproto.xrpc_client.models.com.atproto.admin import defs as ComAtprotoAdminDefs
from atproto.xrpc_client.models.com.atproto.admin import disable_account_invites as ComAtprotoAdminDisableAccountInvites
from atproto.xrpc_client.models.com.atproto.admin import disable_invite_codes as ComAtprotoAdminDisableInviteCodes
from atproto.xrpc_client.models.com.atproto.admin import enable_account_invites as ComAtprotoAdminEnableAccountInvites
from atproto.xrpc_client.models.com.atproto.admin import get_invite_codes as ComAtprotoAdminGetInviteCodes
from atproto.xrpc_client.models.com.atproto.admin import get_moderation_action as ComAtprotoAdminGetModerationAction
from atproto.xrpc_client.models.com.atproto.admin import get_moderation_actions as ComAtprotoAdminGetModerationActions
from atproto.xrpc_client.models.com.atproto.admin import get_moderation_report as ComAtprotoAdminGetModerationReport
from atproto.xrpc_client.models.com.atproto.admin import get_moderation_reports as ComAtprotoAdminGetModerationReports
from atproto.xrpc_client.models.com.atproto.admin import get_record as ComAtprotoAdminGetRecord
from atproto.xrpc_client.models.com.atproto.admin import get_repo as ComAtprotoAdminGetRepo
from atproto.xrpc_client.models.com.atproto.admin import rebase_repo as ComAtprotoAdminRebaseRepo
from atproto.xrpc_client.models.com.atproto.admin import (
    resolve_moderation_reports as ComAtprotoAdminResolveModerationReports,
)
from atproto.xrpc_client.models.com.atproto.admin import (
    reverse_moderation_action as ComAtprotoAdminReverseModerationAction,
)
from atproto.xrpc_client.models.com.atproto.admin import search_repos as ComAtprotoAdminSearchRepos
from atproto.xrpc_client.models.com.atproto.admin import send_email as ComAtprotoAdminSendEmail
from atproto.xrpc_client.models.com.atproto.admin import take_moderation_action as ComAtprotoAdminTakeModerationAction
from atproto.xrpc_client.models.com.atproto.admin import update_account_email as ComAtprotoAdminUpdateAccountEmail
from atproto.xrpc_client.models.com.atproto.admin import update_account_handle as ComAtprotoAdminUpdateAccountHandle
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
from atproto.xrpc_client.models.com.atproto.repo import rebase_repo as ComAtprotoRepoRebaseRepo
from atproto.xrpc_client.models.com.atproto.repo import strong_ref as ComAtprotoRepoStrongRef
from atproto.xrpc_client.models.com.atproto.repo import upload_blob as ComAtprotoRepoUploadBlob
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
from atproto.xrpc_client.models.com.atproto.server import request_password_reset as ComAtprotoServerRequestPasswordReset
from atproto.xrpc_client.models.com.atproto.server import reset_password as ComAtprotoServerResetPassword
from atproto.xrpc_client.models.com.atproto.server import revoke_app_password as ComAtprotoServerRevokeAppPassword
from atproto.xrpc_client.models.com.atproto.sync import get_blob as ComAtprotoSyncGetBlob
from atproto.xrpc_client.models.com.atproto.sync import get_blocks as ComAtprotoSyncGetBlocks
from atproto.xrpc_client.models.com.atproto.sync import get_checkout as ComAtprotoSyncGetCheckout
from atproto.xrpc_client.models.com.atproto.sync import get_commit_path as ComAtprotoSyncGetCommitPath
from atproto.xrpc_client.models.com.atproto.sync import get_head as ComAtprotoSyncGetHead
from atproto.xrpc_client.models.com.atproto.sync import get_record as ComAtprotoSyncGetRecord
from atproto.xrpc_client.models.com.atproto.sync import get_repo as ComAtprotoSyncGetRepo
from atproto.xrpc_client.models.com.atproto.sync import list_blobs as ComAtprotoSyncListBlobs
from atproto.xrpc_client.models.com.atproto.sync import list_repos as ComAtprotoSyncListRepos
from atproto.xrpc_client.models.com.atproto.sync import notify_of_update as ComAtprotoSyncNotifyOfUpdate
from atproto.xrpc_client.models.com.atproto.sync import request_crawl as ComAtprotoSyncRequestCrawl
from atproto.xrpc_client.models.com.atproto.sync import subscribe_repos as ComAtprotoSyncSubscribeRepos
from atproto.xrpc_client.models.utils import get_model_as_dict, get_model_as_json, get_or_create, is_record_type


class _Ids:
    AppBskyEmbedRecordWithMedia: str = 'app.bsky.embed.recordWithMedia'
    AppBskyEmbedImages: str = 'app.bsky.embed.images'
    AppBskyEmbedRecord: str = 'app.bsky.embed.record'
    AppBskyEmbedExternal: str = 'app.bsky.embed.external'
    AppBskyNotificationUpdateSeen: str = 'app.bsky.notification.updateSeen'
    AppBskyNotificationListNotifications: str = 'app.bsky.notification.listNotifications'
    AppBskyNotificationGetUnreadCount: str = 'app.bsky.notification.getUnreadCount'
    AppBskyUnspeccedGetTimelineSkeleton: str = 'app.bsky.unspecced.getTimelineSkeleton'
    AppBskyUnspeccedGetPopularFeedGenerators: str = 'app.bsky.unspecced.getPopularFeedGenerators'
    AppBskyUnspeccedGetPopular: str = 'app.bsky.unspecced.getPopular'
    AppBskyGraphGetLists: str = 'app.bsky.graph.getLists'
    AppBskyGraphListitem: str = 'app.bsky.graph.listitem'
    AppBskyGraphDefs: str = 'app.bsky.graph.defs'
    AppBskyGraphGetFollowers: str = 'app.bsky.graph.getFollowers'
    AppBskyGraphGetBlocks: str = 'app.bsky.graph.getBlocks'
    AppBskyGraphList: str = 'app.bsky.graph.list'
    AppBskyGraphFollow: str = 'app.bsky.graph.follow'
    AppBskyGraphGetListMutes: str = 'app.bsky.graph.getListMutes'
    AppBskyGraphMuteActor: str = 'app.bsky.graph.muteActor'
    AppBskyGraphUnmuteActor: str = 'app.bsky.graph.unmuteActor'
    AppBskyGraphGetList: str = 'app.bsky.graph.getList'
    AppBskyGraphGetMutes: str = 'app.bsky.graph.getMutes'
    AppBskyGraphGetFollows: str = 'app.bsky.graph.getFollows'
    AppBskyGraphMuteActorList: str = 'app.bsky.graph.muteActorList'
    AppBskyGraphBlock: str = 'app.bsky.graph.block'
    AppBskyGraphUnmuteActorList: str = 'app.bsky.graph.unmuteActorList'
    AppBskyFeedGetLikes: str = 'app.bsky.feed.getLikes'
    AppBskyFeedPost: str = 'app.bsky.feed.post'
    AppBskyFeedDefs: str = 'app.bsky.feed.defs'
    AppBskyFeedGetActorFeeds: str = 'app.bsky.feed.getActorFeeds'
    AppBskyFeedGetFeedGenerators: str = 'app.bsky.feed.getFeedGenerators'
    AppBskyFeedGetPostThread: str = 'app.bsky.feed.getPostThread'
    AppBskyFeedGetAuthorFeed: str = 'app.bsky.feed.getAuthorFeed'
    AppBskyFeedGetPosts: str = 'app.bsky.feed.getPosts'
    AppBskyFeedLike: str = 'app.bsky.feed.like'
    AppBskyFeedDescribeFeedGenerator: str = 'app.bsky.feed.describeFeedGenerator'
    AppBskyFeedGenerator: str = 'app.bsky.feed.generator'
    AppBskyFeedGetRepostedBy: str = 'app.bsky.feed.getRepostedBy'
    AppBskyFeedGetTimeline: str = 'app.bsky.feed.getTimeline'
    AppBskyFeedGetFeedSkeleton: str = 'app.bsky.feed.getFeedSkeleton'
    AppBskyFeedGetFeedGenerator: str = 'app.bsky.feed.getFeedGenerator'
    AppBskyFeedRepost: str = 'app.bsky.feed.repost'
    AppBskyFeedGetFeed: str = 'app.bsky.feed.getFeed'
    AppBskyRichtextFacet: str = 'app.bsky.richtext.facet'
    AppBskyActorSearchActors: str = 'app.bsky.actor.searchActors'
    AppBskyActorGetSuggestions: str = 'app.bsky.actor.getSuggestions'
    AppBskyActorDefs: str = 'app.bsky.actor.defs'
    AppBskyActorGetPreferences: str = 'app.bsky.actor.getPreferences'
    AppBskyActorProfile: str = 'app.bsky.actor.profile'
    AppBskyActorPutPreferences: str = 'app.bsky.actor.putPreferences'
    AppBskyActorGetProfiles: str = 'app.bsky.actor.getProfiles'
    AppBskyActorSearchActorsTypeahead: str = 'app.bsky.actor.searchActorsTypeahead'
    AppBskyActorGetProfile: str = 'app.bsky.actor.getProfile'
    ComAtprotoIdentityResolveHandle: str = 'com.atproto.identity.resolveHandle'
    ComAtprotoIdentityUpdateHandle: str = 'com.atproto.identity.updateHandle'
    ComAtprotoAdminUpdateAccountHandle: str = 'com.atproto.admin.updateAccountHandle'
    ComAtprotoAdminGetModerationAction: str = 'com.atproto.admin.getModerationAction'
    ComAtprotoAdminDefs: str = 'com.atproto.admin.defs'
    ComAtprotoAdminGetRepo: str = 'com.atproto.admin.getRepo'
    ComAtprotoAdminDisableInviteCodes: str = 'com.atproto.admin.disableInviteCodes'
    ComAtprotoAdminResolveModerationReports: str = 'com.atproto.admin.resolveModerationReports'
    ComAtprotoAdminGetInviteCodes: str = 'com.atproto.admin.getInviteCodes'
    ComAtprotoAdminGetModerationActions: str = 'com.atproto.admin.getModerationActions'
    ComAtprotoAdminGetRecord: str = 'com.atproto.admin.getRecord'
    ComAtprotoAdminTakeModerationAction: str = 'com.atproto.admin.takeModerationAction'
    ComAtprotoAdminGetModerationReport: str = 'com.atproto.admin.getModerationReport'
    ComAtprotoAdminGetModerationReports: str = 'com.atproto.admin.getModerationReports'
    ComAtprotoAdminRebaseRepo: str = 'com.atproto.admin.rebaseRepo'
    ComAtprotoAdminUpdateAccountEmail: str = 'com.atproto.admin.updateAccountEmail'
    ComAtprotoAdminSendEmail: str = 'com.atproto.admin.sendEmail'
    ComAtprotoAdminEnableAccountInvites: str = 'com.atproto.admin.enableAccountInvites'
    ComAtprotoAdminDisableAccountInvites: str = 'com.atproto.admin.disableAccountInvites'
    ComAtprotoAdminReverseModerationAction: str = 'com.atproto.admin.reverseModerationAction'
    ComAtprotoAdminSearchRepos: str = 'com.atproto.admin.searchRepos'
    ComAtprotoLabelDefs: str = 'com.atproto.label.defs'
    ComAtprotoLabelSubscribeLabels: str = 'com.atproto.label.subscribeLabels'
    ComAtprotoLabelQueryLabels: str = 'com.atproto.label.queryLabels'
    ComAtprotoServerDefs: str = 'com.atproto.server.defs'
    ComAtprotoServerCreateInviteCodes: str = 'com.atproto.server.createInviteCodes'
    ComAtprotoServerDescribeServer: str = 'com.atproto.server.describeServer'
    ComAtprotoServerListAppPasswords: str = 'com.atproto.server.listAppPasswords'
    ComAtprotoServerCreateSession: str = 'com.atproto.server.createSession'
    ComAtprotoServerDeleteSession: str = 'com.atproto.server.deleteSession'
    ComAtprotoServerGetAccountInviteCodes: str = 'com.atproto.server.getAccountInviteCodes'
    ComAtprotoServerRefreshSession: str = 'com.atproto.server.refreshSession'
    ComAtprotoServerGetSession: str = 'com.atproto.server.getSession'
    ComAtprotoServerResetPassword: str = 'com.atproto.server.resetPassword'
    ComAtprotoServerRevokeAppPassword: str = 'com.atproto.server.revokeAppPassword'
    ComAtprotoServerRequestAccountDelete: str = 'com.atproto.server.requestAccountDelete'
    ComAtprotoServerCreateAppPassword: str = 'com.atproto.server.createAppPassword'
    ComAtprotoServerCreateAccount: str = 'com.atproto.server.createAccount'
    ComAtprotoServerCreateInviteCode: str = 'com.atproto.server.createInviteCode'
    ComAtprotoServerDeleteAccount: str = 'com.atproto.server.deleteAccount'
    ComAtprotoServerRequestPasswordReset: str = 'com.atproto.server.requestPasswordReset'
    ComAtprotoSyncListBlobs: str = 'com.atproto.sync.listBlobs'
    ComAtprotoSyncGetHead: str = 'com.atproto.sync.getHead'
    ComAtprotoSyncGetRepo: str = 'com.atproto.sync.getRepo'
    ComAtprotoSyncGetCommitPath: str = 'com.atproto.sync.getCommitPath'
    ComAtprotoSyncGetBlocks: str = 'com.atproto.sync.getBlocks'
    ComAtprotoSyncGetCheckout: str = 'com.atproto.sync.getCheckout'
    ComAtprotoSyncListRepos: str = 'com.atproto.sync.listRepos'
    ComAtprotoSyncGetRecord: str = 'com.atproto.sync.getRecord'
    ComAtprotoSyncGetBlob: str = 'com.atproto.sync.getBlob'
    ComAtprotoSyncRequestCrawl: str = 'com.atproto.sync.requestCrawl'
    ComAtprotoSyncSubscribeRepos: str = 'com.atproto.sync.subscribeRepos'
    ComAtprotoSyncNotifyOfUpdate: str = 'com.atproto.sync.notifyOfUpdate'
    ComAtprotoRepoPutRecord: str = 'com.atproto.repo.putRecord'
    ComAtprotoRepoStrongRef: str = 'com.atproto.repo.strongRef'
    ComAtprotoRepoGetRecord: str = 'com.atproto.repo.getRecord'
    ComAtprotoRepoDescribeRepo: str = 'com.atproto.repo.describeRepo'
    ComAtprotoRepoCreateRecord: str = 'com.atproto.repo.createRecord'
    ComAtprotoRepoListRecords: str = 'com.atproto.repo.listRecords'
    ComAtprotoRepoApplyWrites: str = 'com.atproto.repo.applyWrites'
    ComAtprotoRepoDeleteRecord: str = 'com.atproto.repo.deleteRecord'
    ComAtprotoRepoRebaseRepo: str = 'com.atproto.repo.rebaseRepo'
    ComAtprotoRepoUploadBlob: str = 'com.atproto.repo.uploadBlob'
    ComAtprotoModerationDefs: str = 'com.atproto.moderation.defs'
    ComAtprotoModerationCreateReport: str = 'com.atproto.moderation.createReport'


ids = _Ids()
