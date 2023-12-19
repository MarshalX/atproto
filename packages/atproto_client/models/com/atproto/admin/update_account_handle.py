##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing_extensions as te

from atproto_client.models import base


class Data(base.DataModelBase):

    """Input data model for :obj:`com.atproto.admin.updateAccountHandle`."""

    did: str  #: Did.
    handle: str  #: Handle.


class DataDict(te.TypedDict):
    did: str  #: Did.
    handle: str  #: Handle.
