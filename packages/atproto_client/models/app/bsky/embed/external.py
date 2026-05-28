#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

from pydantic import Field

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
    from atproto_client.models.blob_ref import BlobRef
from atproto_client.models import base


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
