#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base, unknown_union


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`app.bsky.labeler.getServices`."""

    dids: t.List[string_formats.Did]  #: Dids.
    detailed: t.Optional[bool] = False  #: Detailed.


class ParamsDict(t.TypedDict):
    dids: t.List[string_formats.Did]  #: Dids.
    detailed: te.NotRequired[t.Optional[bool]]  #: Detailed.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`app.bsky.labeler.getServices`."""

    views: t.List[
        unknown_union.OpenUnion[
            t.Union['models.AppBskyLabelerDefs.LabelerView', 'models.AppBskyLabelerDefs.LabelerViewDetailed']
        ]
    ]  #: Views.
