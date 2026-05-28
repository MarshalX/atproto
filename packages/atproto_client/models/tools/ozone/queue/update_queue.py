#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Data(base.DataModelBase):
    """Input data model for :obj:`tools.ozone.queue.updateQueue`."""

    queue_id: int  #: ID of the queue to update.
    description: t.Optional[str] = None  #: Optional description of the queue.
    enabled: t.Optional[bool] = None  #: Enable or disable the queue.
    name: t.Optional[str] = None  #: New display name for the queue.


class DataDict(t.TypedDict):
    queue_id: int  #: ID of the queue to update.
    description: te.NotRequired[t.Optional[str]]  #: Optional description of the queue.
    enabled: te.NotRequired[t.Optional[bool]]  #: Enable or disable the queue.
    name: te.NotRequired[t.Optional[str]]  #: New display name for the queue.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.queue.updateQueue`."""

    queue: 'models.ToolsOzoneQueueDefs.QueueView'  #: Queue.
