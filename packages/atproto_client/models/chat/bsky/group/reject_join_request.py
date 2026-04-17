##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

from atproto_client.models import base, string_formats


class Data(base.DataModelBase):
    """Input data model for :obj:`chat.bsky.group.rejectJoinRequest`."""

    convo_id: str  #: Convo id.
    member: string_formats.Did  #: Member.


class DataDict(t.TypedDict):
    convo_id: str  #: Convo id.
    member: string_formats.Did  #: Member.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`chat.bsky.group.rejectJoinRequest`."""
