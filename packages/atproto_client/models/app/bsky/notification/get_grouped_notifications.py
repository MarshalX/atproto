#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base, unknown_union


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`app.bsky.notification.getGroupedNotifications`."""

    cursor: te.Annotated[t.Optional[str], Field(max_length=1024)] = None  #: Cursor.
    feed: te.Annotated[
        t.Optional[t.Union[t.Literal['all', 'people-i-follow', 'conversations', 'followers', 'activity'], str]],
        Field(max_length=32),
    ] = None  #: Which notification feed to return. Grouping behavior varies by feed: notifications about follows might be grouped in 'all' and ungrouped (or rather, in single-item groups) in 'followers'.
    limit: te.Annotated[t.Optional[int], Field(ge=1, le=50)] = None  #: Maximum number of groups to return.


class ParamsDict(t.TypedDict):
    cursor: te.NotRequired[t.Optional[str]]  #: Cursor.
    feed: te.NotRequired[
        t.Optional[t.Union[t.Literal['all', 'people-i-follow', 'conversations', 'followers', 'activity'], str]]
    ]  #: Which notification feed to return. Grouping behavior varies by feed: notifications about follows might be grouped in 'all' and ungrouped (or rather, in single-item groups) in 'followers'.
    limit: te.NotRequired[t.Optional[int]]  #: Maximum number of groups to return.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`app.bsky.notification.getGroupedNotifications`."""

    groups: t.List[
        'models.AppBskyNotificationGetGroupedNotifications.Group'
    ]  #: Notification groups or individual notifications, newest first. Clients should ignore kinds they do not recognize. Grouping behavior depends on the kind and selected feed.
    cursor: te.Annotated[t.Optional[str], Field(max_length=1024)] = None  #: Cursor.
    related_views: t.Optional[
        t.List[
            unknown_union.OpenUnion[
                t.Union[
                    'models.AppBskyActorDefs.ProfileViewDetailed',
                    'models.AppBskyFeedDefs.BlockedPost',
                    'models.AppBskyFeedDefs.GeneratorView',
                    'models.AppBskyFeedDefs.NotFoundPost',
                    'models.AppBskyFeedDefs.PostView',
                    'models.AppBskyGraphDefs.StarterPackView',
                ]
            ]
        ]
    ] = None  #: Reusable views referenced by notifications. Views shared across notifications appear once to avoid duplication. Each group contributes only its first 10 of each related view to this array. Ex: for a group containing likes in a post, we might have a large number of likeItem (e.g., 50) in a group, but only the profile views for the newest 10 items will be included here.
    seen_at: t.Optional[string_formats.DateTime] = None  #: Seen at.


class Group(base.ModelBase):
    """Definition model for :obj:`app.bsky.notification.getGroupedNotifications`. Contains common metadata and kind-specific data for a notification group or individual notification."""

    count: int = Field(ge=1)  #: Count.
    id: str = Field(max_length=256)  #: Id.
    indexed_at: string_formats.DateTime  #: Indexed at.
    is_read: bool  #: Is read.
    kind: unknown_union.OpenUnion[
        t.Union[
            'models.AppBskyNotificationGetGroupedNotifications.LikeGroup',
            'models.AppBskyNotificationGetGroupedNotifications.MultiPostLikeGroup',
            'models.AppBskyNotificationGetGroupedNotifications.RepostGroup',
            'models.AppBskyNotificationGetGroupedNotifications.LikeViaRepostGroup',
            'models.AppBskyNotificationGetGroupedNotifications.RepostViaRepostGroup',
            'models.AppBskyNotificationGetGroupedNotifications.FollowGroup',
            'models.AppBskyNotificationGetGroupedNotifications.SubscribedPostGroup',
            'models.AppBskyNotificationGetGroupedNotifications.GeneratorLikeGroup',
            'models.AppBskyNotificationGetGroupedNotifications.ReplyNotification',
            'models.AppBskyNotificationGetGroupedNotifications.QuoteNotification',
            'models.AppBskyNotificationGetGroupedNotifications.MentionNotification',
            'models.AppBskyNotificationGetGroupedNotifications.FollowBackNotification',
            'models.AppBskyNotificationGetGroupedNotifications.VerifiedNotification',
            'models.AppBskyNotificationGetGroupedNotifications.UnverifiedNotification',
            'models.AppBskyNotificationGetGroupedNotifications.StarterPackJoinedNotification',
            'models.AppBskyNotificationGetGroupedNotifications.ContactMatchNotification',
        ]
    ]  #: Kind.

    py_type: t.Literal['app.bsky.notification.getGroupedNotifications#group'] = Field(
        default='app.bsky.notification.getGroupedNotifications#group', alias='$type', frozen=True
    )


class LikeGroup(base.ModelBase):
    """Definition model for :obj:`app.bsky.notification.getGroupedNotifications`. Group of likes by different actors on the same post."""

    items: t.List['models.AppBskyNotificationGetGroupedNotifications.LikeItem'] = Field(min_length=1)  #: Items.
    post: string_formats.AtUri  #: Post.

    py_type: t.Literal['app.bsky.notification.getGroupedNotifications#likeGroup'] = Field(
        default='app.bsky.notification.getGroupedNotifications#likeGroup', alias='$type', frozen=True
    )


class LikeItem(base.ModelBase):
    """Definition model for :obj:`app.bsky.notification.getGroupedNotifications`. One actor who liked the group's post."""

    actor: string_formats.Did  #: Actor.

    py_type: t.Literal['app.bsky.notification.getGroupedNotifications#likeItem'] = Field(
        default='app.bsky.notification.getGroupedNotifications#likeItem', alias='$type', frozen=True
    )


class MultiPostLikeGroup(base.ModelBase):
    """Definition model for :obj:`app.bsky.notification.getGroupedNotifications`. Group of likes by the same actor on different posts."""

    actor: string_formats.Did  #: Actor.
    items: t.List['models.AppBskyNotificationGetGroupedNotifications.MultiPostLikeItem'] = Field(
        min_length=2
    )  #: Items.

    py_type: t.Literal['app.bsky.notification.getGroupedNotifications#multiPostLikeGroup'] = Field(
        default='app.bsky.notification.getGroupedNotifications#multiPostLikeGroup', alias='$type', frozen=True
    )


class MultiPostLikeItem(base.ModelBase):
    """Definition model for :obj:`app.bsky.notification.getGroupedNotifications`. One post which was liked by the group's actor."""

    post: string_formats.AtUri  #: Post.

    py_type: t.Literal['app.bsky.notification.getGroupedNotifications#multiPostLikeItem'] = Field(
        default='app.bsky.notification.getGroupedNotifications#multiPostLikeItem', alias='$type', frozen=True
    )


class RepostGroup(base.ModelBase):
    """Definition model for :obj:`app.bsky.notification.getGroupedNotifications`. Group of reposts by different actors of the same post."""

    items: t.List['models.AppBskyNotificationGetGroupedNotifications.RepostItem'] = Field(min_length=1)  #: Items.
    post: string_formats.AtUri  #: Post.

    py_type: t.Literal['app.bsky.notification.getGroupedNotifications#repostGroup'] = Field(
        default='app.bsky.notification.getGroupedNotifications#repostGroup', alias='$type', frozen=True
    )


class RepostItem(base.ModelBase):
    """Definition model for :obj:`app.bsky.notification.getGroupedNotifications`. One actor who reposted the group's post."""

    actor: string_formats.Did  #: Actor.

    py_type: t.Literal['app.bsky.notification.getGroupedNotifications#repostItem'] = Field(
        default='app.bsky.notification.getGroupedNotifications#repostItem', alias='$type', frozen=True
    )


class LikeViaRepostGroup(base.ModelBase):
    """Definition model for :obj:`app.bsky.notification.getGroupedNotifications`. Group of likes by different actors on the same post via the requesting account's repost."""

    items: t.List['models.AppBskyNotificationGetGroupedNotifications.LikeViaRepostItem'] = Field(
        min_length=1
    )  #: Items.
    post: string_formats.AtUri  #: Post.
    via_repost: string_formats.AtUri  #: Via repost.

    py_type: t.Literal['app.bsky.notification.getGroupedNotifications#likeViaRepostGroup'] = Field(
        default='app.bsky.notification.getGroupedNotifications#likeViaRepostGroup', alias='$type', frozen=True
    )


class LikeViaRepostItem(base.ModelBase):
    """Definition model for :obj:`app.bsky.notification.getGroupedNotifications`. One actor who liked the group's post via the requesting account's repost."""

    actor: string_formats.Did  #: Actor.

    py_type: t.Literal['app.bsky.notification.getGroupedNotifications#likeViaRepostItem'] = Field(
        default='app.bsky.notification.getGroupedNotifications#likeViaRepostItem', alias='$type', frozen=True
    )


class RepostViaRepostGroup(base.ModelBase):
    """Definition model for :obj:`app.bsky.notification.getGroupedNotifications`. Group of reposts by different actors of the same post via the requesting account's repost."""

    items: t.List['models.AppBskyNotificationGetGroupedNotifications.RepostViaRepostItem'] = Field(
        min_length=1
    )  #: Items.
    post: string_formats.AtUri  #: Post.
    via_repost: string_formats.AtUri  #: Via repost.

    py_type: t.Literal['app.bsky.notification.getGroupedNotifications#repostViaRepostGroup'] = Field(
        default='app.bsky.notification.getGroupedNotifications#repostViaRepostGroup', alias='$type', frozen=True
    )


class RepostViaRepostItem(base.ModelBase):
    """Definition model for :obj:`app.bsky.notification.getGroupedNotifications`. One actor who reposted the group's post via the requesting account's repost."""

    actor: string_formats.Did  #: Actor.

    py_type: t.Literal['app.bsky.notification.getGroupedNotifications#repostViaRepostItem'] = Field(
        default='app.bsky.notification.getGroupedNotifications#repostViaRepostItem', alias='$type', frozen=True
    )


class FollowGroup(base.ModelBase):
    """Definition model for :obj:`app.bsky.notification.getGroupedNotifications`. Group of actors who followed the requesting account."""

    items: t.List['models.AppBskyNotificationGetGroupedNotifications.FollowItem'] = Field(min_length=1)  #: Items.

    py_type: t.Literal['app.bsky.notification.getGroupedNotifications#followGroup'] = Field(
        default='app.bsky.notification.getGroupedNotifications#followGroup', alias='$type', frozen=True
    )


class FollowItem(base.ModelBase):
    """Definition model for :obj:`app.bsky.notification.getGroupedNotifications`. An actor who followed the requesting account, possibly via a starter pack."""

    actor: string_formats.Did  #: Actor.
    starter_pack: t.Optional[string_formats.AtUri] = None  #: Starter pack.

    py_type: t.Literal['app.bsky.notification.getGroupedNotifications#followItem'] = Field(
        default='app.bsky.notification.getGroupedNotifications#followItem', alias='$type', frozen=True
    )


class SubscribedPostGroup(base.ModelBase):
    """Definition model for :obj:`app.bsky.notification.getGroupedNotifications`. Group of new posts by actors the requesting account subscribes to."""

    items: t.List['models.AppBskyNotificationGetGroupedNotifications.SubscribedPostItem'] = Field(
        min_length=1
    )  #: Items.

    py_type: t.Literal['app.bsky.notification.getGroupedNotifications#subscribedPostGroup'] = Field(
        default='app.bsky.notification.getGroupedNotifications#subscribedPostGroup', alias='$type', frozen=True
    )


class SubscribedPostItem(base.ModelBase):
    """Definition model for :obj:`app.bsky.notification.getGroupedNotifications`. One new post by an actor the requesting account subscribes to."""

    actor: string_formats.Did  #: Actor.
    post: string_formats.AtUri  #: Post.

    py_type: t.Literal['app.bsky.notification.getGroupedNotifications#subscribedPostItem'] = Field(
        default='app.bsky.notification.getGroupedNotifications#subscribedPostItem', alias='$type', frozen=True
    )


class GeneratorLikeGroup(base.ModelBase):
    """Definition model for :obj:`app.bsky.notification.getGroupedNotifications`. Group of likes by different actors on the same feed generator."""

    generator: string_formats.AtUri  #: Generator.
    items: t.List['models.AppBskyNotificationGetGroupedNotifications.GeneratorLikeItem'] = Field(
        min_length=1
    )  #: Items.

    py_type: t.Literal['app.bsky.notification.getGroupedNotifications#generatorLikeGroup'] = Field(
        default='app.bsky.notification.getGroupedNotifications#generatorLikeGroup', alias='$type', frozen=True
    )


class GeneratorLikeItem(base.ModelBase):
    """Definition model for :obj:`app.bsky.notification.getGroupedNotifications`. One actor who liked the feed generator in the group."""

    actor: string_formats.Did  #: Actor.

    py_type: t.Literal['app.bsky.notification.getGroupedNotifications#generatorLikeItem'] = Field(
        default='app.bsky.notification.getGroupedNotifications#generatorLikeItem', alias='$type', frozen=True
    )


class ReplyNotification(base.ModelBase):
    """Definition model for :obj:`app.bsky.notification.getGroupedNotifications`. A reply to a post by the requesting account or to a thread they are participating in."""

    parent: string_formats.AtUri  #: Parent.
    post: string_formats.AtUri  #: Post.

    py_type: t.Literal['app.bsky.notification.getGroupedNotifications#replyNotification'] = Field(
        default='app.bsky.notification.getGroupedNotifications#replyNotification', alias='$type', frozen=True
    )


class QuoteNotification(base.ModelBase):
    """Definition model for :obj:`app.bsky.notification.getGroupedNotifications`. A post quoting a post by the requesting account."""

    post: string_formats.AtUri  #: Post.
    parent: t.Optional[string_formats.AtUri] = None  #: Parent.

    py_type: t.Literal['app.bsky.notification.getGroupedNotifications#quoteNotification'] = Field(
        default='app.bsky.notification.getGroupedNotifications#quoteNotification', alias='$type', frozen=True
    )


class MentionNotification(base.ModelBase):
    """Definition model for :obj:`app.bsky.notification.getGroupedNotifications`. A post mentioning the requesting account."""

    post: string_formats.AtUri  #: Post.
    parent: t.Optional[string_formats.AtUri] = None  #: Parent.

    py_type: t.Literal['app.bsky.notification.getGroupedNotifications#mentionNotification'] = Field(
        default='app.bsky.notification.getGroupedNotifications#mentionNotification', alias='$type', frozen=True
    )


class FollowBackNotification(base.ModelBase):
    """Definition model for :obj:`app.bsky.notification.getGroupedNotifications`. An actor followed the requesting account back, possibly via a starter pack."""

    actor: string_formats.Did  #: Actor.
    starter_pack: t.Optional[string_formats.AtUri] = None  #: Starter pack.

    py_type: t.Literal['app.bsky.notification.getGroupedNotifications#followBackNotification'] = Field(
        default='app.bsky.notification.getGroupedNotifications#followBackNotification', alias='$type', frozen=True
    )


class VerifiedNotification(base.ModelBase):
    """Definition model for :obj:`app.bsky.notification.getGroupedNotifications`. An actor verified the requesting account."""

    actor: string_formats.Did  #: Actor.

    py_type: t.Literal['app.bsky.notification.getGroupedNotifications#verifiedNotification'] = Field(
        default='app.bsky.notification.getGroupedNotifications#verifiedNotification', alias='$type', frozen=True
    )


class UnverifiedNotification(base.ModelBase):
    """Definition model for :obj:`app.bsky.notification.getGroupedNotifications`. A verification of the requesting account was removed."""

    actor: string_formats.Did  #: Actor.

    py_type: t.Literal['app.bsky.notification.getGroupedNotifications#unverifiedNotification'] = Field(
        default='app.bsky.notification.getGroupedNotifications#unverifiedNotification', alias='$type', frozen=True
    )


class StarterPackJoinedNotification(base.ModelBase):
    """Definition model for :obj:`app.bsky.notification.getGroupedNotifications`. An actor joined Bluesky via a starter pack created by the requesting account."""

    actor: string_formats.Did  #: Actor.
    starter_pack: string_formats.AtUri  #: Starter pack.

    py_type: t.Literal['app.bsky.notification.getGroupedNotifications#starterPackJoinedNotification'] = Field(
        default='app.bsky.notification.getGroupedNotifications#starterPackJoinedNotification',
        alias='$type',
        frozen=True,
    )


class ContactMatchNotification(base.ModelBase):
    """Definition model for :obj:`app.bsky.notification.getGroupedNotifications`. A contact of the requesting account joined Bluesky."""

    actor: string_formats.Did  #: Actor.

    py_type: t.Literal['app.bsky.notification.getGroupedNotifications#contactMatchNotification'] = Field(
        default='app.bsky.notification.getGroupedNotifications#contactMatchNotification', alias='$type', frozen=True
    )
