##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


from dataclasses import dataclass

from atproto.xrpc_client.models import base


@dataclass
class Main(base.ModelBase):

    """Definition model for :obj:`com.atproto.repo.strongRef`.

    Attributes:
        uri: Uri.
        cid: Cid.
    """

    cid: str
    uri: str

    _type: str = 'com.atproto.repo.strongRef'
