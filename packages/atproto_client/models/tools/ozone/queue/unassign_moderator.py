##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

from atproto_client.models import base, string_formats


class Data(base.DataModelBase):
    """Input data model for :obj:`tools.ozone.queue.unassignModerator`."""

    did: string_formats.Did  #: DID to be unassigned.
    queue_id: int  #: The ID of the queue to unassign the user from.


class DataDict(t.TypedDict):
    did: string_formats.Did  #: DID to be unassigned.
    queue_id: int  #: The ID of the queue to unassign the user from.
