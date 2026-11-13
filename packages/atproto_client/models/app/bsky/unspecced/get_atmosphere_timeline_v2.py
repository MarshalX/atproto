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
    """Parameters model for :obj:`app.bsky.unspecced.getAtmosphereTimelineV2`."""

    cursor: t.Optional[str] = None  #: Cursor.


class ParamsDict(t.TypedDict):
    cursor: te.NotRequired[t.Optional[str]]  #: Cursor.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`app.bsky.unspecced.getAtmosphereTimelineV2`."""

    feed: t.List[
        unknown_union.OpenUnion[
            t.Union[
                'models.AppBskyUnspeccedGetAtmosphereTimelineV2.ActivityItem',
                'models.AppBskyUnspeccedGetAtmosphereTimelineV2.ActivityActorGroup',
                'models.AppBskyUnspeccedGetAtmosphereTimelineV2.ActivitySubjectGroup',
            ]
        ]
    ]  #: Activities and activity groups, sorted newest first by indexedAt. Groups and relatedActivity only contain activities from the same page of results. Activities by actors unavailable to the viewer are omitted before grouping. Clients should ignore entry types they do not recognize.
    related_views: t.List[
        unknown_union.OpenUnion['models.AppBskyActorDefs.ProfileViewBasic']
    ]  #: Reusable views referenced by feed entries. Views shared across entries appear once to avoid duplication. Always includes the profile of the actor of every activityItem and activityActorGroup, plus the profiles of at most the newest 3 distinct actors in each activitySubjectGroup and in each collection of an activityItem's relatedActivity. Ex: for a subject group of 12 recommendations, only the profiles of the 3 newest recommenders are included; clients can fetch the rest with app.bsky.actor.getProfiles.
    cursor: t.Optional[str] = None  #: Cursor.


class ActivityItem(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.getAtmosphereTimelineV2`. A single activity with its hydrated subject. An activity that creates content, such as publishing an article, is always a standalone item when other activities on the same page target that content; those activities are attached as relatedActivity. Activities whose subject is unavailable to the viewer are omitted from the timeline."""

    actor: string_formats.Did  #: Actor.
    collection: string_formats.Nsid  #: The collection of the activity record. Ex: site.standard.graph.recommend.
    indexed_at: string_formats.DateTime  #: When the activity was indexed. Determines the item's position in the feed, even when relatedActivity contains newer activities.
    ref: 'models.ComAtprotoRepoStrongRef.Main'  #: Ref.
    subject: 'models.AppBskyUnspeccedGetAtmosphereTimelineV2.ActivitySubject'  #: Subject.
    related_activity: t.Optional[
        t.List['models.AppBskyUnspeccedGetAtmosphereTimelineV2.ActivityItemRelatedActivity']
    ] = None  #: All available activities on the same page that target content created by this activity, newest first. Ex: recommendations of a newly published article. Only present on activities that create content. Activities targeting content created on an earlier page appear as their own feed entries instead.

    py_type: t.Literal['app.bsky.unspecced.getAtmosphereTimelineV2#activityItem'] = Field(
        default='app.bsky.unspecced.getAtmosphereTimelineV2#activityItem', alias='$type', frozen=True
    )


class ActivityItemRelatedActivity(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.getAtmosphereTimelineV2`."""

    actor: string_formats.Did  #: Actor.
    collection: string_formats.Nsid  #: Collection.
    indexed_at: string_formats.DateTime  #: Indexed at.
    ref: 'models.ComAtprotoRepoStrongRef.Main'  #: Ref.

    py_type: t.Literal['app.bsky.unspecced.getAtmosphereTimelineV2#activityItemRelatedActivity'] = Field(
        default='app.bsky.unspecced.getAtmosphereTimelineV2#activityItemRelatedActivity', alias='$type', frozen=True
    )


class ActivitySubject(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.getAtmosphereTimelineV2`. The hydrated content an activity targets. For activities that create content, such as publishing an article, the subject is the created record itself."""

    ref: 'models.ComAtprotoRepoStrongRef.Main'  #: The record backing the view. Ex: the site.standard.document of an article.
    view: unknown_union.OpenUnion[
        t.Union[
            'models.AppBskyEmbedExternal.ViewArticle',
            'models.AppBskyEmbedExternal.ViewArticlePublication',
            'models.AppBskyEmbedExternal.ViewGallery',
            'models.AppBskyEmbedExternal.ViewLivestream',
        ]
    ]  #: View.
    bsky_post_ref: t.Optional['models.ComAtprotoRepoStrongRef.Main'] = (
        None  #: The Bluesky post associated with the subject, as declared by its author. The referenced post may not be available.
    )
    bsky_post_view: t.Optional['models.AppBskyFeedDefs.PostView'] = (
        None  #: The hydrated Bluesky post associated with the subject. Omitted when the post is unavailable to the viewer. May reflect a newer version of the post than the CID in bskyPostRef.
    )

    py_type: t.Literal['app.bsky.unspecced.getAtmosphereTimelineV2#activitySubject'] = Field(
        default='app.bsky.unspecced.getAtmosphereTimelineV2#activitySubject', alias='$type', frozen=True
    )


class ActivityActorGroup(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.getAtmosphereTimelineV2`. Activities by one actor in one collection close together in time, such as several articles published by the same author. Activities that create content with relatedActivity are never grouped. Positioned in the feed at its newest activity."""

    activities: t.List['models.AppBskyUnspeccedGetAtmosphereTimelineV2.ActivityActorGroupItem'] = Field(
        min_length=2
    )  #: All activities in the group, newest first.
    actor: string_formats.Did  #: Actor.
    collection: string_formats.Nsid  #: Collection.
    indexed_at: string_formats.DateTime  #: When the group's newest activity was indexed.
    subjects: t.List['models.AppBskyUnspeccedGetAtmosphereTimelineV2.ActivitySubject'] = Field(
        min_length=1
    )  #: Hydrated subjects of the group's activities, newest first. Currently only the newest subject is included; clients can hydrate the rest from the subject URIs in activities.

    py_type: t.Literal['app.bsky.unspecced.getAtmosphereTimelineV2#activityActorGroup'] = Field(
        default='app.bsky.unspecced.getAtmosphereTimelineV2#activityActorGroup', alias='$type', frozen=True
    )


class ActivityActorGroupItem(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.getAtmosphereTimelineV2`."""

    indexed_at: string_formats.DateTime  #: Indexed at.
    ref: 'models.ComAtprotoRepoStrongRef.Main'  #: Ref.
    subject: (
        string_formats.AtUri
    )  #: The content the activity targets. Matches ref.uri for activities that create content.

    py_type: t.Literal['app.bsky.unspecced.getAtmosphereTimelineV2#activityActorGroupItem'] = Field(
        default='app.bsky.unspecced.getAtmosphereTimelineV2#activityActorGroupItem', alias='$type', frozen=True
    )


class ActivitySubjectGroup(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.getAtmosphereTimelineV2`. Activities by at least two actors in one collection targeting the same subject, such as several recommendations of an article published on an earlier page. Positioned in the feed at its newest activity."""

    activities: t.List['models.AppBskyUnspeccedGetAtmosphereTimelineV2.ActivitySubjectGroupItem'] = Field(
        min_length=2
    )  #: All activities in the group, newest first.
    collection: string_formats.Nsid  #: Collection.
    indexed_at: string_formats.DateTime  #: When the group's newest activity was indexed.
    subject: 'models.AppBskyUnspeccedGetAtmosphereTimelineV2.ActivitySubject'  #: Subject.

    py_type: t.Literal['app.bsky.unspecced.getAtmosphereTimelineV2#activitySubjectGroup'] = Field(
        default='app.bsky.unspecced.getAtmosphereTimelineV2#activitySubjectGroup', alias='$type', frozen=True
    )


class ActivitySubjectGroupItem(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.getAtmosphereTimelineV2`."""

    actor: string_formats.Did  #: Actor.
    indexed_at: string_formats.DateTime  #: Indexed at.
    ref: 'models.ComAtprotoRepoStrongRef.Main'  #: Ref.

    py_type: t.Literal['app.bsky.unspecced.getAtmosphereTimelineV2#activitySubjectGroupItem'] = Field(
        default='app.bsky.unspecced.getAtmosphereTimelineV2#activitySubjectGroupItem', alias='$type', frozen=True
    )
