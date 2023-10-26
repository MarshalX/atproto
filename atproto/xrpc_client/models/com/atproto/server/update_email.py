##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te

from atproto.xrpc_client.models import base


class Data(base.DataModelBase):

    """Input data model for :obj:`com.atproto.server.updateEmail`."""

    email: str  #: Email.
    token: t.Optional[
        str
    ] = None  #: Requires a token from com.atproto.sever.requestEmailUpdate if the account's email has been confirmed.


class DataDict(te.TypedDict):
    email: str  #: Email.
    token: te.NotRequired[
        t.Optional[str]
    ]  #: Requires a token from com.atproto.sever.requestEmailUpdate if the account's email has been confirmed.
