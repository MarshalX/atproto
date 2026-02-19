##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class DraftWithId(base.ModelBase):
    """Definition model for :obj:`app.bsky.draft.defs`. A draft with an identifier, used to store drafts in private storage (stash)."""

    draft: 'models.AppBskyDraftDefs.Draft'  #: Draft.
    id: string_formats.Tid  #: A TID to be used as a draft identifier.

    py_type: t.Literal['app.bsky.draft.defs#draftWithId'] = Field(
        default='app.bsky.draft.defs#draftWithId', alias='$type', frozen=True
    )


class Draft(base.ModelBase):
    """Definition model for :obj:`app.bsky.draft.defs`. A draft containing an array of draft posts."""

    posts: t.List['models.AppBskyDraftDefs.DraftPost'] = Field(
        min_length=1, max_length=100
    )  #: Array of draft posts that compose this draft.
    device_id: te.Annotated[t.Optional[str], Field(max_length=100)] = (
        None  #: UUIDv4 identifier of the device that created this draft.
    )
    device_name: te.Annotated[t.Optional[str], Field(max_length=100)] = (
        None  #: The device and/or platform on which the draft was created.
    )
    langs: te.Annotated[t.Optional[t.List[string_formats.Language]], Field(max_length=3)] = (
        None  #: Indicates human language of posts primary text content.
    )
    postgate_embedding_rules: t.Optional[
        t.List[te.Annotated[t.Union['models.AppBskyFeedPostgate.DisableRule'], Field(discriminator='py_type')]]
    ] = Field(max_length=5)  #: Embedding rules for the postgates to be created when this draft is published.
    threadgate_allow: t.Optional[
        t.List[
            te.Annotated[
                t.Union[
                    'models.AppBskyFeedThreadgate.MentionRule',
                    'models.AppBskyFeedThreadgate.FollowerRule',
                    'models.AppBskyFeedThreadgate.FollowingRule',
                    'models.AppBskyFeedThreadgate.ListRule',
                ],
                Field(discriminator='py_type'),
            ]
        ]
    ] = Field(max_length=5)  #: Allow-rules for the threadgate to be created when this draft is published.

    py_type: t.Literal['app.bsky.draft.defs#draft'] = Field(
        default='app.bsky.draft.defs#draft', alias='$type', frozen=True
    )


class DraftPost(base.ModelBase):
    """Definition model for :obj:`app.bsky.draft.defs`. One of the posts that compose a draft."""

    text: str = Field(
        max_length=10000
    )  #: The primary post content. It has a higher limit than post contents to allow storing a larger text that can later be refined into smaller posts.
    embed_externals: te.Annotated[
        t.Optional[t.List['models.AppBskyDraftDefs.DraftEmbedExternal']], Field(max_length=1)
    ] = None  #: Embed externals.
    embed_images: te.Annotated[t.Optional[t.List['models.AppBskyDraftDefs.DraftEmbedImage']], Field(max_length=4)] = (
        None  #: Embed images.
    )
    embed_records: te.Annotated[t.Optional[t.List['models.AppBskyDraftDefs.DraftEmbedRecord']], Field(max_length=1)] = (
        None  #: Embed records.
    )
    embed_videos: te.Annotated[t.Optional[t.List['models.AppBskyDraftDefs.DraftEmbedVideo']], Field(max_length=1)] = (
        None  #: Embed videos.
    )
    labels: t.Optional[
        te.Annotated[t.Union['models.ComAtprotoLabelDefs.SelfLabels'], Field(discriminator='py_type')]
    ] = None  #: Self-label values for this post. Effectively content warnings.

    py_type: t.Literal['app.bsky.draft.defs#draftPost'] = Field(
        default='app.bsky.draft.defs#draftPost', alias='$type', frozen=True
    )


class DraftView(base.ModelBase):
    """Definition model for :obj:`app.bsky.draft.defs`. View to present drafts data to users."""

    created_at: string_formats.DateTime  #: The time the draft was created.
    draft: 'models.AppBskyDraftDefs.Draft'  #: Draft.
    id: string_formats.Tid  #: A TID to be used as a draft identifier.
    updated_at: string_formats.DateTime  #: The time the draft was last updated.

    py_type: t.Literal['app.bsky.draft.defs#draftView'] = Field(
        default='app.bsky.draft.defs#draftView', alias='$type', frozen=True
    )


class DraftEmbedLocalRef(base.ModelBase):
    """Definition model for :obj:`app.bsky.draft.defs`."""

    path: str = Field(
        min_length=1, max_length=1024
    )  #: Local, on-device ref to file to be embedded. Embeds are currently device-bound for drafts.

    py_type: t.Literal['app.bsky.draft.defs#draftEmbedLocalRef'] = Field(
        default='app.bsky.draft.defs#draftEmbedLocalRef', alias='$type', frozen=True
    )


class DraftEmbedCaption(base.ModelBase):
    """Definition model for :obj:`app.bsky.draft.defs`."""

    content: str = Field(max_length=10000)  #: Content.
    lang: string_formats.Language  #: Lang.

    py_type: t.Literal['app.bsky.draft.defs#draftEmbedCaption'] = Field(
        default='app.bsky.draft.defs#draftEmbedCaption', alias='$type', frozen=True
    )


class DraftEmbedImage(base.ModelBase):
    """Definition model for :obj:`app.bsky.draft.defs`."""

    local_ref: 'models.AppBskyDraftDefs.DraftEmbedLocalRef'  #: Local ref.
    alt: t.Optional[str] = None  #: Alt.

    py_type: t.Literal['app.bsky.draft.defs#draftEmbedImage'] = Field(
        default='app.bsky.draft.defs#draftEmbedImage', alias='$type', frozen=True
    )


class DraftEmbedVideo(base.ModelBase):
    """Definition model for :obj:`app.bsky.draft.defs`."""

    local_ref: 'models.AppBskyDraftDefs.DraftEmbedLocalRef'  #: Local ref.
    alt: t.Optional[str] = None  #: Alt.
    captions: te.Annotated[t.Optional[t.List['models.AppBskyDraftDefs.DraftEmbedCaption']], Field(max_length=20)] = (
        None  #: Captions.
    )

    py_type: t.Literal['app.bsky.draft.defs#draftEmbedVideo'] = Field(
        default='app.bsky.draft.defs#draftEmbedVideo', alias='$type', frozen=True
    )


class DraftEmbedExternal(base.ModelBase):
    """Definition model for :obj:`app.bsky.draft.defs`."""

    uri: string_formats.Uri  #: Uri.

    py_type: t.Literal['app.bsky.draft.defs#draftEmbedExternal'] = Field(
        default='app.bsky.draft.defs#draftEmbedExternal', alias='$type', frozen=True
    )


class DraftEmbedRecord(base.ModelBase):
    """Definition model for :obj:`app.bsky.draft.defs`."""

    record: 'models.ComAtprotoRepoStrongRef.Main'  #: Record.

    py_type: t.Literal['app.bsky.draft.defs#draftEmbedRecord'] = Field(
        default='app.bsky.draft.defs#draftEmbedRecord', alias='$type', frozen=True
    )
