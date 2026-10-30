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
                'models.AppBskyUnspeccedGetAtmosphereTimeline.ActivityItemOverflow',
                'models.AppBskyUnspeccedGetAtmosphereTimeline.ActivityGroup',
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
                'models.AppBskyUnspeccedGetAtmosphereTimeline.ActivityItemOverflow',
                'models.AppBskyUnspeccedGetAtmosphereTimeline.ActivityGroup',
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
    related_activity: t.Optional[t.List['models.AppBskyUnspeccedGetAtmosphereTimeline.ActivityItem']] = (
        None  #: Recommendations and shares attached to this article. Attached activities do not themselves contain related activity.
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

    py_type: t.Literal['app.bsky.unspecced.getAtmosphereTimeline#activityItem'] = Field(
        default='app.bsky.unspecced.getAtmosphereTimeline#activityItem', alias='$type', frozen=True
    )


class ActivityItemOverflow(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.getAtmosphereTimeline`. Distinct additional activities omitted from this page for an author and collection, without hydrating the omitted records."""

    associated_profiles: t.List['models.AppBskyActorDefs.ProfileViewBasic']  #: Associated profiles.
    collection: string_formats.Nsid  #: Collection.
    count: int = Field(ge=1)  #: Count.

    py_type: t.Literal['app.bsky.unspecced.getAtmosphereTimeline#activityItemOverflow'] = Field(
        default='app.bsky.unspecced.getAtmosphereTimeline#activityItemOverflow', alias='$type', frozen=True
    )


class ActivityGroup(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.getAtmosphereTimeline`. Two or more activities of the same collection, within a fixed window anchored at the newest member. The group occupies the newest member's position."""

    collection: string_formats.Nsid  #: Collection.
    group_by: t.Union[t.Literal['subject', 'actor'], str]  #: Group by.
    id: str  #: Id.
    indexed_at: string_formats.DateTime  #: Indexed at.
    items: t.List['models.AppBskyUnspeccedGetAtmosphereTimeline.ActivityItem'] = Field(min_length=2)  #: Items.
    actor: t.Optional[string_formats.Did] = None  #: Actor.
    subject: t.Optional[string_formats.AtUri] = None  #: Subject.

    py_type: t.Literal['app.bsky.unspecced.getAtmosphereTimeline#activityGroup'] = Field(
        default='app.bsky.unspecced.getAtmosphereTimeline#activityGroup', alias='$type', frozen=True
    )
