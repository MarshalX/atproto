##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te

from atproto_client.models import base, string_formats


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`com.atproto.sync.getRecord`."""

    collection: string_formats.Nsid  #: Collection.
    did: string_formats.Did  #: The DID of the repo.
    rkey: str  #: Record Key.
    commit: t.Optional[string_formats.Cid] = (
        None  #: DEPRECATED: referenced a repo commit by CID, and retrieved record as of that commit.
    )


class ParamsDict(t.TypedDict):
    collection: string_formats.Nsid  #: Collection.
    did: string_formats.Did  #: The DID of the repo.
    rkey: str  #: Record Key.
    commit: te.NotRequired[
        t.Optional[string_formats.Cid]
    ]  #: DEPRECATED: referenced a repo commit by CID, and retrieved record as of that commit.


#: Response raw data type.
Response: te.TypeAlias = bytes
