#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

from atproto_client.models import base


class Data(base.DataModelBase):
    """Input data model for :obj:`chat.bsky.group.withdrawJoinRequest`."""

    convo_id: str  #: Convo id.


class DataDict(t.TypedDict):
    convo_id: str  #: Convo id.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`chat.bsky.group.withdrawJoinRequest`."""
