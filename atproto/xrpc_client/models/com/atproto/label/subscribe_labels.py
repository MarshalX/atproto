##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


from dataclasses import dataclass
from typing import List, Optional

from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


@dataclass
class Labels(base.ModelBase):

    """Definition model for :obj:`com.atproto.label.subscribeLabels`.

    Attributes:
        seq: Seq.
        labels: Labels.
    """

    labels: List['models.ComAtprotoLabelDefs.Label']
    seq: int


@dataclass
class Info(base.ModelBase):

    """Definition model for :obj:`com.atproto.label.subscribeLabels`.

    Attributes:
        name: Name.
        message: Message.
    """

    name: str
    message: Optional[str] = None
