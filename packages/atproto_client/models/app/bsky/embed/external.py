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
    from atproto_client.models.blob_ref import BlobRef
from atproto_client.models import base, unknown_union


class Main(base.ModelBase):
    """Definition model for :obj:`app.bsky.embed.external`. A representation of some externally linked content (eg, a URL and 'card'), embedded in a Bluesky record (eg, a post)."""

    external: 'models.AppBskyEmbedExternal.External'  #: External.

    py_type: t.Literal['app.bsky.embed.external'] = Field(default='app.bsky.embed.external', alias='$type', frozen=True)


class External(base.ModelBase):
    """Definition model for :obj:`app.bsky.embed.external`."""

    description: str  #: Description.
    title: str  #: Title.
    uri: string_formats.Uri  #: Uri.
    associated_refs: t.Optional[t.List['models.ComAtprotoRepoStrongRef.Main']] = (
        None  #: StrongRefs (uri+cid) of the Atmosphere records that backed this view.
    )
    thumb: t.Optional['BlobRef'] = None  #: Thumb.

    py_type: t.Literal['app.bsky.embed.external#external'] = Field(
        default='app.bsky.embed.external#external', alias='$type', frozen=True
    )


class View(base.ModelBase):
    """Definition model for :obj:`app.bsky.embed.external`."""

    external: 'models.AppBskyEmbedExternal.ViewExternal'  #: External.

    py_type: t.Literal['app.bsky.embed.external#view'] = Field(
        default='app.bsky.embed.external#view', alias='$type', frozen=True
    )


class ViewExternal(base.ModelBase):
    """Definition model for :obj:`app.bsky.embed.external`."""

    description: str  #: Description.
    title: str  #: Title.
    uri: string_formats.Uri  #: Uri.
    associated_profiles: t.Optional[t.List['models.AppBskyActorDefs.ProfileViewBasic']] = (
        None  #: Profiles of the owners of the Atmosphere records that backed this view.
    )
    associated_refs: t.Optional[t.List['models.ComAtprotoRepoStrongRef.Main']] = (
        None  #: StrongRefs (uri+cid) of the Atmosphere records that backed this view.
    )
    created_at: t.Optional[string_formats.DateTime] = (
        None  #: When the external content was created, if available. Example: a publication date, for an article.
    )
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.
    reading_time: t.Optional[int] = None  #: Estimated reading time in minutes, if applicable and available.
    source: t.Optional['models.AppBskyEmbedExternal.ViewExternalSource'] = None  #: Source.
    thumb: t.Optional[string_formats.Uri] = None  #: Thumb.
    updated_at: t.Optional[string_formats.DateTime] = None  #: When the external content was updated, if available.

    py_type: t.Literal['app.bsky.embed.external#viewExternal'] = Field(
        default='app.bsky.embed.external#viewExternal', alias='$type', frozen=True
    )


class ViewExternalSource(base.ModelBase):
    """Definition model for :obj:`app.bsky.embed.external`. The source of an external embed, such as a standard.site publication."""

    title: str  #: Title.
    uri: (
        string_formats.Uri
    )  #: URI of the source, if available. Example: the https:// URL of a site.standard.publication record.
    description: t.Optional[str] = None  #: Description.
    icon: t.Optional[string_formats.Uri] = (
        None  #: Fully-qualified URL where an icon representing the source can be fetched. For example, CDN location provided by the App View.
    )
    theme: t.Optional['models.AppBskyEmbedExternal.ViewExternalSourceTheme'] = None  #: Theme.

    py_type: t.Literal['app.bsky.embed.external#viewExternalSource'] = Field(
        default='app.bsky.embed.external#viewExternalSource', alias='$type', frozen=True
    )


class ViewExternalSourceTheme(base.ModelBase):
    """Definition model for :obj:`app.bsky.embed.external`. The theme colors of an external source, such as a site.standard.publication. These colors may be used when rendering an embed from that source."""

    accent_foreground_rgb: t.Optional['models.AppBskyEmbedExternal.ColorRGB'] = None  #: Accent foreground r g b.
    accent_rgb: t.Optional['models.AppBskyEmbedExternal.ColorRGB'] = None  #: Accent r g b.
    background_rgb: t.Optional['models.AppBskyEmbedExternal.ColorRGB'] = None  #: Background r g b.
    foreground_rgb: t.Optional['models.AppBskyEmbedExternal.ColorRGB'] = None  #: Foreground r g b.

    py_type: t.Literal['app.bsky.embed.external#viewExternalSourceTheme'] = Field(
        default='app.bsky.embed.external#viewExternalSourceTheme', alias='$type', frozen=True
    )


class ColorRGB(base.ModelBase):
    """Definition model for :obj:`app.bsky.embed.external`. RGB color definition, inspired by site.standard.theme.color#rgb."""

    b: int = Field(ge=0, le=255)  #: B.
    g: int = Field(ge=0, le=255)  #: G.
    r: int = Field(ge=0, le=255)  #: R.

    py_type: t.Literal['app.bsky.embed.external#colorRGB'] = Field(
        default='app.bsky.embed.external#colorRGB', alias='$type', frozen=True
    )


class ViewArticle(base.ModelBase):
    """Definition model for :obj:`app.bsky.embed.external`."""

    description: str  #: Description.
    title: str  #: Title.
    uri: string_formats.Uri  #: Uri.
    associated_profiles: t.Optional[t.List['models.AppBskyActorDefs.ProfileViewBasic']] = None  #: Associated profiles.
    associated_refs: t.Optional[t.List['models.ComAtprotoRepoStrongRef.Main']] = None  #: Associated refs.
    created_at: t.Optional[string_formats.DateTime] = None  #: Created at.
    image: t.Optional[string_formats.Uri] = None  #: Image.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.
    like_count: te.Annotated[t.Optional[int], Field(ge=0)] = None  #: Like count.
    likers: te.Annotated[t.Optional[t.List['models.AppBskyActorDefs.ProfileViewBasic']], Field(max_length=3)] = (
        None  #: Available profile previews. Selected deterministically by DID; not a ranking.
    )
    publisher: t.Optional['models.AppBskyEmbedExternal.ViewArticlePublication'] = None  #: Publisher.
    reading_time: te.Annotated[t.Optional[int], Field(ge=1)] = None  #: Reading time.
    updated_at: t.Optional[string_formats.DateTime] = None  #: Updated at.

    py_type: t.Literal['app.bsky.embed.external#viewArticle'] = Field(
        default='app.bsky.embed.external#viewArticle', alias='$type', frozen=True
    )


class ViewArticlePublication(base.ModelBase):
    """Definition model for :obj:`app.bsky.embed.external`."""

    description: str  #: Description.
    title: str  #: Title.
    uri: string_formats.Uri  #: Uri.
    associated_profiles: t.Optional[t.List['models.AppBskyActorDefs.ProfileViewBasic']] = None  #: Associated profiles.
    associated_refs: t.Optional[t.List['models.ComAtprotoRepoStrongRef.Main']] = None  #: Associated refs.
    created_at: t.Optional[string_formats.DateTime] = None  #: Created at.
    image: t.Optional[string_formats.Uri] = None  #: Image.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.
    logo: t.Optional[string_formats.Uri] = None  #: Logo.
    subscribers: te.Annotated[t.Optional[t.List['models.AppBskyActorDefs.ProfileViewBasic']], Field(max_length=3)] = (
        None  #: Available profile previews. Selected deterministically by DID; not a ranking.
    )
    subscription_count: te.Annotated[t.Optional[int], Field(ge=0)] = None  #: Subscription count.
    theme: t.Optional['models.AppBskyEmbedExternal.ViewArticlePublicationTheme'] = None  #: Theme.
    updated_at: t.Optional[string_formats.DateTime] = None  #: Updated at.

    py_type: t.Literal['app.bsky.embed.external#viewArticlePublication'] = Field(
        default='app.bsky.embed.external#viewArticlePublication', alias='$type', frozen=True
    )


class ViewArticlePublicationTheme(base.ModelBase):
    """Definition model for :obj:`app.bsky.embed.external`."""

    accent: t.Optional[str] = None  #: Hex color string, if available. Example: '#ffffff'.
    accent_foreground: t.Optional[str] = None  #: Hex color string, if available. Example: '#ffffff'.
    background: t.Optional[str] = None  #: Hex color string, if available. Example: '#ffffff'.
    foreground: t.Optional[str] = None  #: Hex color string, if available. Example: '#ffffff'.

    py_type: t.Literal['app.bsky.embed.external#viewArticlePublicationTheme'] = Field(
        default='app.bsky.embed.external#viewArticlePublicationTheme', alias='$type', frozen=True
    )


class ViewGallery(base.ModelBase):
    """Definition model for :obj:`app.bsky.embed.external`."""

    description: str  #: Description.
    items: t.List[
        unknown_union.OpenUnion['models.AppBskyEmbedExternal.ViewGalleryImage']
    ]  #: The media items in the gallery. Each item may be of a different type, but all types must be supported by the client.
    title: str  #: Title.
    uri: string_formats.Uri  #: Uri.
    associated_profiles: t.Optional[t.List['models.AppBskyActorDefs.ProfileViewBasic']] = None  #: Associated profiles.
    associated_refs: t.Optional[t.List['models.ComAtprotoRepoStrongRef.Main']] = None  #: Associated refs.
    created_at: t.Optional[string_formats.DateTime] = None  #: Created at.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.
    like_count: te.Annotated[t.Optional[int], Field(ge=0)] = None  #: Like count.
    likers: te.Annotated[t.Optional[t.List['models.AppBskyActorDefs.ProfileViewBasic']], Field(max_length=3)] = (
        None  #: Available profile previews. Selected deterministically by DID; not a ranking.
    )
    updated_at: t.Optional[string_formats.DateTime] = None  #: Updated at.

    py_type: t.Literal['app.bsky.embed.external#viewGallery'] = Field(
        default='app.bsky.embed.external#viewGallery', alias='$type', frozen=True
    )


class ViewGalleryImage(base.ModelBase):
    """Definition model for :obj:`app.bsky.embed.external`."""

    fullsize: string_formats.Uri  #: Fully-qualified URL where a large version of the image can be fetched. May or may not be the exact original blob. For example, CDN location provided by the App View.
    thumbnail: string_formats.Uri  #: Fully-qualified URL where a thumbnail of the image can be fetched. For example, CDN location provided by the App View.
    alt: t.Optional[str] = None  #: Alt text description of the image, for accessibility.
    aspect_ratio: t.Optional['models.AppBskyEmbedDefs.AspectRatio'] = None  #: Aspect ratio.

    py_type: t.Literal['app.bsky.embed.external#viewGalleryImage'] = Field(
        default='app.bsky.embed.external#viewGalleryImage', alias='$type', frozen=True
    )


class ViewLivestream(base.ModelBase):
    """Definition model for :obj:`app.bsky.embed.external`."""

    active: bool  #: True if the livestream is currently active at the time this view is served, false if it has ended.
    description: str  #: Description.
    title: str  #: Title.
    uri: string_formats.Uri  #: Uri.
    associated_profiles: t.Optional[t.List['models.AppBskyActorDefs.ProfileViewBasic']] = None  #: Associated profiles.
    associated_refs: t.Optional[t.List['models.ComAtprotoRepoStrongRef.Main']] = None  #: Associated refs.
    created_at: t.Optional[string_formats.DateTime] = None  #: Created at.
    ended_at: t.Optional[string_formats.DateTime] = None  #: Ended at.
    image: t.Optional[string_formats.Uri] = None  #: Image.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.
    started_at: t.Optional[string_formats.DateTime] = None  #: Started at.
    updated_at: t.Optional[string_formats.DateTime] = None  #: Updated at.

    py_type: t.Literal['app.bsky.embed.external#viewLivestream'] = Field(
        default='app.bsky.embed.external#viewLivestream', alias='$type', frozen=True
    )
