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
    """Parameters model for :obj:`app.bsky.unspecced.getAtmosphereTimeline`."""

    cursor: t.Optional[str] = None  #: Cursor.


class ParamsDict(t.TypedDict):
    cursor: te.NotRequired[t.Optional[str]]  #: Cursor.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`app.bsky.unspecced.getAtmosphereTimeline`."""

    feed: t.List[
        unknown_union.OpenUnion[
            t.Union[
                'models.AppBskyUnspeccedGetAtmosphereTimeline.ActivityItem',
                'models.AppBskyUnspeccedGetAtmosphereTimeline.ActivityActorGroup',
                'models.AppBskyUnspeccedGetAtmosphereTimeline.ActivitySubjectGroup',
            ]
        ]
    ]  #: Feed.
    cursor: t.Optional[str] = None  #: Cursor.

    def get_page_items(
        self,
    ) -> t.List[
        unknown_union.OpenUnion[
            t.Union[
                'models.AppBskyUnspeccedGetAtmosphereTimeline.ActivityItem',
                'models.AppBskyUnspeccedGetAtmosphereTimeline.ActivityActorGroup',
                'models.AppBskyUnspeccedGetAtmosphereTimeline.ActivitySubjectGroup',
            ]
        ]
    ]:
        """Get the items of this page."""
        return self.feed


class ActivityRecord(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.getAtmosphereTimeline`."""

    cid: string_formats.Cid  #: Cid.
    indexed_at: string_formats.DateTime  #: Indexed at.
    uri: string_formats.AtUri  #: Uri.

    py_type: t.Literal['app.bsky.unspecced.getAtmosphereTimeline#activityRecord'] = Field(
        default='app.bsky.unspecced.getAtmosphereTimeline#activityRecord', alias='$type', frozen=True
    )


class ViewerState(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.getAtmosphereTimeline`."""

    subscribed: bool  #: Subscribed.

    py_type: t.Literal['app.bsky.unspecced.getAtmosphereTimeline#viewerState'] = Field(
        default='app.bsky.unspecced.getAtmosphereTimeline#viewerState', alias='$type', frozen=True
    )


class ActivityItem(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.getAtmosphereTimeline`."""

    collection: string_formats.Nsid  #: Collection.
    record: 'models.AppBskyUnspeccedGetAtmosphereTimeline.ActivityRecord'  #: Record.
    viewer_state: 'models.AppBskyUnspeccedGetAtmosphereTimeline.ViewerState'  #: Viewer state.
    bsky_post_ref: t.Optional['models.ComAtprotoRepoStrongRef.Main'] = (
        None  #: The Bluesky post associated with the rendered article or livestream, as declared by its author. The referenced post may not be available.
    )
    related_activity: t.Optional[t.List['models.AppBskyUnspeccedGetAtmosphereTimeline.ActivityRelatedGroup']] = (
        None  #: Collection-specific activity references targeting this item's record. Article creations with related activity remain standalone; only the parent item's view is hydrated.
    )
    view: t.Optional[
        unknown_union.OpenUnion[
            t.Union[
                'models.AppBskyEmbedExternal.ViewArticle',
                'models.AppBskyEmbedExternal.ViewArticlePublication',
                'models.AppBskyEmbedExternal.ViewGallery',
                'models.AppBskyEmbedExternal.ViewLivestream',
                'models.AppBskyFeedDefs.PostView',
            ]
        ]
    ] = None  #: View.
    view_bsky_post: t.Optional['models.AppBskyFeedDefs.PostView'] = (
        None  #: The hydrated Bluesky post associated with the rendered article or livestream, as declared by its author. Omitted when the post is unavailable to the viewer.
    )

    py_type: t.Literal['app.bsky.unspecced.getAtmosphereTimeline#activityItem'] = Field(
        default='app.bsky.unspecced.getAtmosphereTimeline#activityItem', alias='$type', frozen=True
    )


class ActivityActorGroup(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.getAtmosphereTimeline`. Activities by one actor in one collection, positioned at the newest group item. Only the newest item is hydrated. Article creations with related activity remain standalone."""

    actor: string_formats.Did  #: Actor.
    collection: string_formats.Nsid  #: Collection.
    id: str  #: Id.
    indexed_at: string_formats.DateTime  #: Indexed at.
    item: 'models.AppBskyUnspeccedGetAtmosphereTimeline.ActivityItem'  #: Item.
    uris: t.List[string_formats.AtUri] = Field(
        min_length=2
    )  #: All visible group item URIs, including the hydrated item, in newest-first timeline order.

    py_type: t.Literal['app.bsky.unspecced.getAtmosphereTimeline#activityActorGroup'] = Field(
        default='app.bsky.unspecced.getAtmosphereTimeline#activityActorGroup', alias='$type', frozen=True
    )


class ActivitySubject(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.getAtmosphereTimeline`. The shared target of grouped activities, not an activity itself."""

    uri: string_formats.AtUri  #: Uri.
    view: unknown_union.OpenUnion[
        t.Union[
            'models.AppBskyEmbedExternal.ViewArticle',
            'models.AppBskyEmbedExternal.ViewArticlePublication',
            'models.AppBskyEmbedExternal.ViewGallery',
        ]
    ]  #: View.
    viewer_state: 'models.AppBskyUnspeccedGetAtmosphereTimeline.ViewerState'  #: Viewer state.
    bsky_post_ref: t.Optional['models.ComAtprotoRepoStrongRef.Main'] = (
        None  #: The author's declared Bluesky post for the target. The post may be unavailable.
    )
    view_bsky_post: t.Optional['models.AppBskyFeedDefs.PostView'] = (
        None  #: The hydrated Bluesky post declared by the target's author. Omitted when the post is unavailable to the viewer.
    )

    py_type: t.Literal['app.bsky.unspecced.getAtmosphereTimeline#activitySubject'] = Field(
        default='app.bsky.unspecced.getAtmosphereTimeline#activitySubject', alias='$type', frozen=True
    )


class ActivityGroupItem(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.getAtmosphereTimeline`. An unhydrated group item. Its actor DID is the authority of its record URI."""

    collection: string_formats.Nsid  #: Collection.
    record: 'models.AppBskyUnspeccedGetAtmosphereTimeline.ActivityRecord'  #: Record.

    py_type: t.Literal['app.bsky.unspecced.getAtmosphereTimeline#activityGroupItem'] = Field(
        default='app.bsky.unspecced.getAtmosphereTimeline#activityGroupItem', alias='$type', frozen=True
    )


class ActivityRelatedGroup(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.getAtmosphereTimeline`. Visible activities in one collection targeting the parent item's record, without a time window. Contains references and profiles only, not a shared subject or hydrated action views. Buckets follow newest-first first appearance."""

    activities: t.List['models.AppBskyUnspeccedGetAtmosphereTimeline.ActivityGroupItem'] = Field(
        min_length=1
    )  #: Visible activity references in newest-first timeline order. Every activity has the bucket's collection.
    actors: t.List['models.AppBskyActorDefs.ProfileViewBasic'] = Field(
        min_length=1
    )  #: Unique actors in first-appearance order among the bucket's activities.
    collection: string_formats.Nsid  #: Collection.

    py_type: t.Literal['app.bsky.unspecced.getAtmosphereTimeline#activityRelatedGroup'] = Field(
        default='app.bsky.unspecced.getAtmosphereTimeline#activityRelatedGroup', alias='$type', frozen=True
    )


class ActivitySubjectGroup(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.getAtmosphereTimeline`. Activities in one collection sharing a target, by at least two distinct actors, positioned at the newest group item. Article recommendations and shares group separately across the returned page without a time window. Article creations are not subject-group items. Publication subscriptions and gallery favorites retain age-based grouping windows."""

    activities: t.List['models.AppBskyUnspeccedGetAtmosphereTimeline.ActivityGroupItem'] = Field(
        min_length=2
    )  #: Visible group items in newest-first timeline order. Every activity has the group's collection.
    actors: t.List['models.AppBskyActorDefs.ProfileViewBasic'] = Field(
        min_length=2
    )  #: Unique actors in first-appearance order among group items. At least two distinct actors are required.
    collection: string_formats.Nsid  #: Collection.
    id: str  #: Id.
    indexed_at: string_formats.DateTime  #: Indexed at.
    subject: 'models.AppBskyUnspeccedGetAtmosphereTimeline.ActivitySubject'  #: Subject.

    py_type: t.Literal['app.bsky.unspecced.getAtmosphereTimeline#activitySubjectGroup'] = Field(
        default='app.bsky.unspecced.getAtmosphereTimeline#activitySubjectGroup', alias='$type', frozen=True
    )
