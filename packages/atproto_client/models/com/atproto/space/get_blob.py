#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te

from atproto_client.models import base, string_formats


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`com.atproto.space.getBlob`."""

    cid: string_formats.Cid  #: Cid.
    repo: string_formats.Did  #: Repo.
    space: string_formats.SpaceRef  #: Space.


class ParamsDict(t.TypedDict):
    cid: string_formats.Cid  #: Cid.
    repo: string_formats.Did  #: Repo.
    space: string_formats.SpaceRef  #: Space.


#: Response raw data type.
Response: te.TypeAlias = bytes
