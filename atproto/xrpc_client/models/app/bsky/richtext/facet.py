##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t
from dataclasses import dataclass

from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


@dataclass
class Main(base.ModelBase):

    """Definition model for :obj:`app.bsky.richtext.facet`."""

    features: t.List[
        t.Union['models.AppBskyRichtextFacet.Mention', 'models.AppBskyRichtextFacet.Link', 't.Dict[str, t.Any]']
    ]  #: Features.
    index: 'models.AppBskyRichtextFacet.ByteSlice'  #: Index.

    _type: str = 'app.bsky.richtext.facet'


@dataclass
class Mention(base.ModelBase):

    """Definition model for :obj:`app.bsky.richtext.facet`. A facet feature for actor mentions."""

    did: str  #: Did.

    _type: str = 'app.bsky.richtext.facet#mention'


@dataclass
class Link(base.ModelBase):

    """Definition model for :obj:`app.bsky.richtext.facet`. A facet feature for links."""

    uri: str  #: Uri.

    _type: str = 'app.bsky.richtext.facet#link'


@dataclass
class ByteSlice(base.ModelBase):

    """Definition model for :obj:`app.bsky.richtext.facet`. A text segment. Start is inclusive, end is exclusive. Indices are for utf8-encoded strings."""

    byteEnd: int  #: Byte end.
    byteStart: int  #: Byte start.

    _type: str = 'app.bsky.richtext.facet#byteSlice'
