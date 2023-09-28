##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


class Main(base.ModelBase):

    """Definition model for :obj:`app.bsky.richtext.facet`."""

    features: t.List[
        te.Annotated[
            t.Union[
                'models.AppBskyRichtextFacet.Mention',
                'models.AppBskyRichtextFacet.Link',
                'models.AppBskyRichtextFacet.Tag',
            ],
            Field(discriminator='py_type'),
        ]
    ]  #: Features.
    index: 'models.AppBskyRichtextFacet.ByteSlice'  #: Index.

    py_type: te.Literal['app.bsky.richtext.facet'] = Field(
        default='app.bsky.richtext.facet', alias='$type', frozen=True
    )


class Mention(base.ModelBase):

    """Definition model for :obj:`app.bsky.richtext.facet`. A facet feature for actor mentions."""

    did: str  #: Did.

    py_type: te.Literal['app.bsky.richtext.facet#mention'] = Field(
        default='app.bsky.richtext.facet#mention', alias='$type', frozen=True
    )


class Link(base.ModelBase):

    """Definition model for :obj:`app.bsky.richtext.facet`. A facet feature for links."""

    uri: str  #: Uri.

    py_type: te.Literal['app.bsky.richtext.facet#link'] = Field(
        default='app.bsky.richtext.facet#link', alias='$type', frozen=True
    )


class Tag(base.ModelBase):

    """Definition model for :obj:`app.bsky.richtext.facet`. A hashtag."""

    tag: str = Field(max_length=640)  #: Tag.

    py_type: te.Literal['app.bsky.richtext.facet#tag'] = Field(
        default='app.bsky.richtext.facet#tag', alias='$type', frozen=True
    )


class ByteSlice(base.ModelBase):

    """Definition model for :obj:`app.bsky.richtext.facet`. A text segment. Start is inclusive, end is exclusive. Indices are for utf8-encoded strings."""

    byte_end: int = Field(alias='byteEnd', ge=0)  #: Byte end.
    byte_start: int = Field(alias='byteStart', ge=0)  #: Byte start.

    py_type: te.Literal['app.bsky.richtext.facet#byteSlice'] = Field(
        default='app.bsky.richtext.facet#byteSlice', alias='$type', frozen=True
    )
