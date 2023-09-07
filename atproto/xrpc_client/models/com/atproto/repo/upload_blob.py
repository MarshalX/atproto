##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te

if t.TYPE_CHECKING:
    from atproto.xrpc_client.models.blob_ref import BlobRef
from atproto.xrpc_client.models import base

#: Data raw data type.
Data: te.TypeAlias = bytes


class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.repo.uploadBlob`."""

    blob: 'BlobRef'  #: Blob.
