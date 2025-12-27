##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

from atproto_client.models import base, string_formats


class Data(base.DataModelBase):
    """Input data model for :obj:`app.bsky.contact.sendNotification`."""

    from_: string_formats.Did  #: The DID of who this notification comes from.
    to: string_formats.Did  #: The DID of who this notification should go to.


class DataDict(t.TypedDict):
    from_: string_formats.Did  #: The DID of who this notification comes from.
    to: string_formats.Did  #: The DID of who this notification should go to.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`app.bsky.contact.sendNotification`."""
