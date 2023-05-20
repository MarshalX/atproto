##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t
from dataclasses import dataclass

from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


@dataclass
class Labels(base.ModelBase):

    """Definition model for :obj:`com.atproto.label.subscribeLabels`.

    Attributes:
        seq: Seq.
        labels: Labels.
    """

    labels: t.List['models.ComAtprotoLabelDefs.Label']
    seq: int

    _type: str = 'com.atproto.label.subscribeLabels#labels'


@dataclass
class Info(base.ModelBase):

    """Definition model for :obj:`com.atproto.label.subscribeLabels`.

    Attributes:
        name: Name.
        message: Message.
    """

    name: str
    message: t.Optional[str] = None

    _type: str = 'com.atproto.label.subscribeLabels#info'
