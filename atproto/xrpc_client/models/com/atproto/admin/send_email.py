##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

from atproto.xrpc_client.models import base


class Data(base.DataModelBase):

    """Input data model for :obj:`com.atproto.admin.sendEmail`."""

    content: str  #: Content.
    recipient_did: str = Field(alias='recipientDid')  #: Recipient did.
    sender_did: str = Field(alias='senderDid')  #: Sender did.
    subject: t.Optional[str] = None  #: Subject.


class DataDict(te.TypedDict):
    content: str  #: Content.
    recipient_did: str  #: Recipient did.
    sender_did: str  #: Sender did.
    subject: te.NotRequired[t.Optional[str]]  #: Subject.


class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.admin.sendEmail`."""

    sent: bool  #: Sent.
