#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

from atproto_client.models import base


class Data(base.DataModelBase):
    """Input data model for :obj:`tools.ozone.queue.assignModerator`."""

    did: str  #: DID to be assigned.
    queue_id: int  #: The ID of the queue to assign the user to.


class DataDict(t.TypedDict):
    did: str  #: DID to be assigned.
    queue_id: int  #: The ID of the queue to assign the user to.
