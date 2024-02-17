##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te

from atproto_client.models import base


class Data(base.DataModelBase):
    """Input data model for :obj:`com.atproto.admin.sendEmail`."""

    content: str  #: Content.
    recipient_did: str  #: Recipient did.
    sender_did: str  #: Sender did.
    comment: t.Optional[
        str
    ] = None  #: Additional comment by the sender that won't be used in the email itself but helpful to provide more context for moderators/reviewers.
    subject: t.Optional[str] = None  #: Subject.


class DataDict(te.TypedDict):
    content: str  #: Content.
    recipient_did: str  #: Recipient did.
    sender_did: str  #: Sender did.
    comment: te.NotRequired[
        t.Optional[str]
    ]  #: Additional comment by the sender that won't be used in the email itself but helpful to provide more context for moderators/reviewers.
    subject: te.NotRequired[t.Optional[str]]  #: Subject.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`com.atproto.admin.sendEmail`."""

    sent: bool  #: Sent.
