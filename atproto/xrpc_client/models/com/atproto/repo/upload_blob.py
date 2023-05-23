##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t
from dataclasses import dataclass

from atproto.xrpc_client.models import base
from atproto.xrpc_client.models.blob_ref import BlobRef

#: Data raw data type.
Data: t.Union[t.Type[str], t.Type[bytes]] = bytes


@dataclass
class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.repo.uploadBlob`."""

    blob: BlobRef  #: Blob.
