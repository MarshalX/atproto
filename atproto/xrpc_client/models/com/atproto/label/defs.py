##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


from dataclasses import dataclass
from typing import Optional

from atproto.xrpc_client.models import base


@dataclass
class Label(base.ModelBase):

    """Definition model for :obj:`com.atproto.label.defs`. Metadata tag on an atproto resource (eg, repo or record)

    Attributes:
        src: DID of the actor who created this label.
        uri: AT URI of the record, repository (account), or other resource which this label applies to.
        cid: optionally, CID specifying the specific version of 'uri' resource this label applies to.
        val: the short string name of the value or type of this label.
        neg: if true, this is a negation label, overwriting a previous label.
        cts: timestamp when this label was created.
    """

    cts: str
    src: str
    uri: str
    val: str
    cid: Optional[str] = None
    neg: Optional[bool] = None
