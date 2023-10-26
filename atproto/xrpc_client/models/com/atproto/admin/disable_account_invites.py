##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te

from atproto.xrpc_client.models import base


class Data(base.DataModelBase):

    """Input data model for :obj:`com.atproto.admin.disableAccountInvites`."""

    account: str  #: Account.
    note: t.Optional[str] = None  #: Additionally add a note describing why the invites were disabled.


class DataDict(te.TypedDict):
    account: str  #: Account.
    note: te.NotRequired[t.Optional[str]]  #: Additionally add a note describing why the invites were disabled.
