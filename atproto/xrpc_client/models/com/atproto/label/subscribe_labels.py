##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

if t.TYPE_CHECKING:
    from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


class Params(base.ParamsModelBase):

    """Parameters model for :obj:`com.atproto.label.subscribeLabels`."""

    cursor: t.Optional[int] = None  #: The last known event to backfill from.


class Labels(base.ModelBase):

    """Definition model for :obj:`com.atproto.label.subscribeLabels`."""

    labels: t.List['models.ComAtprotoLabelDefs.Label']  #: Labels.
    seq: int  #: Seq.

    _type: str = 'com.atproto.label.subscribeLabels#labels'


class Info(base.ModelBase):

    """Definition model for :obj:`com.atproto.label.subscribeLabels`."""

    name: str  #: Name.
    message: t.Optional[str] = None  #: Message.

    _type: str = 'com.atproto.label.subscribeLabels#info'
