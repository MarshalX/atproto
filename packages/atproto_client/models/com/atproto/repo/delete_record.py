##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te

from atproto_client.models import base


class Data(base.DataModelBase):
    """Input data model for :obj:`com.atproto.repo.deleteRecord`."""

    collection: str  #: The NSID of the record collection.
    repo: str  #: The handle or DID of the repo (aka, current account).
    rkey: str  #: The Record Key.
    swap_commit: t.Optional[str] = None  #: Compare and swap with the previous commit by CID.
    swap_record: t.Optional[str] = None  #: Compare and swap with the previous record by CID.


class DataDict(te.TypedDict):
    collection: str  #: The NSID of the record collection.
    repo: str  #: The handle or DID of the repo (aka, current account).
    rkey: str  #: The Record Key.
    swap_commit: te.NotRequired[t.Optional[str]]  #: Compare and swap with the previous commit by CID.
    swap_record: te.NotRequired[t.Optional[str]]  #: Compare and swap with the previous record by CID.
