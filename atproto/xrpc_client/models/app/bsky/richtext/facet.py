##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


from dataclasses import dataclass
from typing import Any, Dict, List, Union

from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


@dataclass
class Main(base.ModelBase):

    """Definition model for :obj:`app.bsky.richtext.facet`.

    Attributes:
        index: Index.
        features: Features.
    """

    features: List[Union['models.AppBskyRichtextFacet.Mention', 'models.AppBskyRichtextFacet.Link', 'Dict[str, Any]']]
    index: 'models.AppBskyRichtextFacet.ByteSlice'

    _type: str = 'app.bsky.richtext.facet'


@dataclass
class Mention(base.ModelBase):

    """Definition model for :obj:`app.bsky.richtext.facet`. A facet feature for actor mentions.

    Attributes:
        did: Did.
    """

    did: str


@dataclass
class Link(base.ModelBase):

    """Definition model for :obj:`app.bsky.richtext.facet`. A facet feature for links.

    Attributes:
        uri: Uri.
    """

    uri: str


@dataclass
class ByteSlice(base.ModelBase):

    """Definition model for :obj:`app.bsky.richtext.facet`. A text segment. Start is inclusive, end is exclusive. Indices are for utf8-encoded strings.

    Attributes:
        byteStart: Byte start.
        byteEnd: Byte end.
    """

    byteEnd: int
    byteStart: int
