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
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`app.bsky.unspecced.getAtmosphereExploreTab`."""

    langs: t.Optional[t.List[string_formats.Language]] = (
        None  #: Preferred languages for article and photo gallery recommendations when their algorithmic recommendations are enabled. Ignored otherwise.
    )


class ParamsDict(t.TypedDict):
    langs: te.NotRequired[
        t.Optional[t.List[string_formats.Language]]
    ]  #: Preferred languages for article and photo gallery recommendations when their algorithmic recommendations are enabled. Ignored otherwise.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`app.bsky.unspecced.getAtmosphereExploreTab`."""

    apps: t.List['models.AppBskyUnspeccedGetAtmosphereExploreTab.AppCard'] = Field(max_length=100)  #: Apps.
    articles: 'models.AppBskyUnspeccedGetAtmosphereExploreTab.ArticleList'  #: Articles.
    livestreams: 'models.AppBskyUnspeccedGetAtmosphereExploreTab.LivestreamList'  #: Livestreams.
    photos: 'models.AppBskyUnspeccedGetAtmosphereExploreTab.GalleryList'  #: Photos.
    publications: 'models.AppBskyUnspeccedGetAtmosphereExploreTab.PublicationList'  #: Publications.
    announcement_banner: t.Optional['models.AppBskyUnspeccedGetAtmosphereExploreTab.AnnouncementBanner'] = (
        None  #: Announcement banner.
    )


class ArticleList(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.getAtmosphereExploreTab`."""

    items: t.List['models.AppBskyUnspeccedGetAtmosphereExploreTab.ArticleItem']  #: Items.
    rec_id_str: t.Optional[str] = (
        None  #: Snowflake for this list's recommendation, use when submitting recommendation events. Omitted when the list is not algorithmically recommended.
    )

    py_type: t.Literal['app.bsky.unspecced.getAtmosphereExploreTab#articleList'] = Field(
        default='app.bsky.unspecced.getAtmosphereExploreTab#articleList', alias='$type', frozen=True
    )


class PublicationList(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.getAtmosphereExploreTab`."""

    items: t.List['models.AppBskyUnspeccedGetAtmosphereExploreTab.PublicationItem']  #: Items.
    rec_id_str: t.Optional[str] = (
        None  #: Snowflake for this list's recommendation, use when submitting recommendation events. Omitted when the list is not algorithmically recommended.
    )

    py_type: t.Literal['app.bsky.unspecced.getAtmosphereExploreTab#publicationList'] = Field(
        default='app.bsky.unspecced.getAtmosphereExploreTab#publicationList', alias='$type', frozen=True
    )


class GalleryList(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.getAtmosphereExploreTab`."""

    items: t.List['models.AppBskyUnspeccedGetAtmosphereExploreTab.GalleryItem']  #: Items.
    rec_id_str: t.Optional[str] = (
        None  #: Snowflake for this list's recommendation, use when submitting recommendation events. Omitted when the list is not algorithmically recommended.
    )

    py_type: t.Literal['app.bsky.unspecced.getAtmosphereExploreTab#galleryList'] = Field(
        default='app.bsky.unspecced.getAtmosphereExploreTab#galleryList', alias='$type', frozen=True
    )


class LivestreamList(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.getAtmosphereExploreTab`."""

    items: t.List['models.AppBskyUnspeccedGetAtmosphereExploreTab.LivestreamItem']  #: Items.
    rec_id_str: t.Optional[str] = (
        None  #: Snowflake for this list's recommendation, use when submitting recommendation events. Omitted when the list is not algorithmically recommended.
    )

    py_type: t.Literal['app.bsky.unspecced.getAtmosphereExploreTab#livestreamList'] = Field(
        default='app.bsky.unspecced.getAtmosphereExploreTab#livestreamList', alias='$type', frozen=True
    )


class ArticleItem(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.getAtmosphereExploreTab`."""

    featured: bool  #: Deprecated. Retained for compatibility; always false.
    view: 'models.AppBskyEmbedExternal.ViewArticle'  #: View.
    bsky_post_ref: t.Optional['models.ComAtprotoRepoStrongRef.Main'] = (
        None  #: The Bluesky post associated with the article, as declared by its author. The referenced post may not be available.
    )
    view_bsky_post: t.Optional['models.AppBskyFeedDefs.PostView'] = (
        None  #: The hydrated Bluesky post associated with the article, as declared by its author. Omitted when the post is unavailable to the viewer.
    )

    py_type: t.Literal['app.bsky.unspecced.getAtmosphereExploreTab#articleItem'] = Field(
        default='app.bsky.unspecced.getAtmosphereExploreTab#articleItem', alias='$type', frozen=True
    )


class PublicationItem(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.getAtmosphereExploreTab`."""

    featured: bool  #: Deprecated. Retained for compatibility; always false.
    view: 'models.AppBskyEmbedExternal.ViewArticlePublication'  #: View.

    py_type: t.Literal['app.bsky.unspecced.getAtmosphereExploreTab#publicationItem'] = Field(
        default='app.bsky.unspecced.getAtmosphereExploreTab#publicationItem', alias='$type', frozen=True
    )


class GalleryItem(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.getAtmosphereExploreTab`."""

    featured: bool  #: Deprecated. Retained for compatibility; always false.
    view: 'models.AppBskyEmbedExternal.ViewGallery'  #: View.

    py_type: t.Literal['app.bsky.unspecced.getAtmosphereExploreTab#galleryItem'] = Field(
        default='app.bsky.unspecced.getAtmosphereExploreTab#galleryItem', alias='$type', frozen=True
    )


class LivestreamItem(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.getAtmosphereExploreTab`."""

    featured: bool  #: Deprecated. Retained for compatibility; always false.
    view: 'models.AppBskyEmbedExternal.ViewLivestream'  #: View.
    bsky_post_ref: t.Optional['models.ComAtprotoRepoStrongRef.Main'] = (
        None  #: The Bluesky post that announced the livestream, as declared by its author. The referenced post may not be available.
    )
    view_bsky_post: t.Optional['models.AppBskyFeedDefs.PostView'] = (
        None  #: The hydrated Bluesky post that announced the livestream, as declared by its author. Omitted when the post is unavailable to the viewer.
    )

    py_type: t.Literal['app.bsky.unspecced.getAtmosphereExploreTab#livestreamItem'] = Field(
        default='app.bsky.unspecced.getAtmosphereExploreTab#livestreamItem', alias='$type', frozen=True
    )


class AnnouncementBanner(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.getAtmosphereExploreTab`."""

    description: te.Annotated[t.Optional[str], Field(max_length=4096)] = None  #: Description.
    id: te.Annotated[t.Optional[str], Field(max_length=4096)] = None  #: Id.
    image: te.Annotated[t.Optional[string_formats.Uri], Field(max_length=4096)] = None  #: Image.
    overlay_color: te.Annotated[t.Optional[str], Field(max_length=4096)] = None  #: Overlay color.
    text_color: te.Annotated[t.Optional[str], Field(max_length=4096)] = None  #: Text color.
    title: te.Annotated[t.Optional[str], Field(max_length=4096)] = None  #: Title.
    url: te.Annotated[t.Optional[string_formats.Uri], Field(max_length=4096)] = None  #: Url.

    py_type: t.Literal['app.bsky.unspecced.getAtmosphereExploreTab#announcementBanner'] = Field(
        default='app.bsky.unspecced.getAtmosphereExploreTab#announcementBanner', alias='$type', frozen=True
    )


class AppCard(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.getAtmosphereExploreTab`."""

    background_image: te.Annotated[t.Optional[string_formats.Uri], Field(max_length=4096)] = (
        None  #: Compatibility field. The profile banner when available, otherwise the editorial background image.
    )
    category: te.Annotated[t.Optional[str], Field(max_length=4096)] = None  #: Category.
    description: te.Annotated[t.Optional[str], Field(max_length=4096)] = None  #: Description.
    id: te.Annotated[t.Optional[str], Field(max_length=4096)] = None  #: Id.
    logo: te.Annotated[t.Optional[string_formats.Uri], Field(max_length=4096)] = (
        None  #: Compatibility field. The profile avatar when available, otherwise the editorial logo.
    )
    overlay_color: te.Annotated[t.Optional[str], Field(max_length=4096)] = (
        None  #: Deprecated. Retained for compatibility.
    )
    profile: t.Optional['models.AppBskyActorDefs.ProfileViewDetailed'] = (
        None  #: The app's account profile, when available.
    )
    text_color: te.Annotated[t.Optional[str], Field(max_length=4096)] = None  #: Deprecated. Retained for compatibility.
    title: te.Annotated[t.Optional[str], Field(max_length=4096)] = None  #: Title.
    url: te.Annotated[t.Optional[string_formats.Uri], Field(max_length=4096)] = None  #: Url.

    py_type: t.Literal['app.bsky.unspecced.getAtmosphereExploreTab#appCard'] = Field(
        default='app.bsky.unspecced.getAtmosphereExploreTab#appCard', alias='$type', frozen=True
    )
