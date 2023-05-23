##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t
from dataclasses import dataclass

from atproto.xrpc_client.models import base


@dataclass
class Label(base.ModelBase):

    """Definition model for :obj:`com.atproto.label.defs`. Metadata tag on an atproto resource (eg, repo or record)"""

    cts: str  #: timestamp when this label was created.
    src: str  #: DID of the actor who created this label.
    uri: str  #: AT URI of the record, repository (account), or other resource which this label applies to.
    val: str  #: the short string name of the value or type of this label.
    cid: t.Optional[
        str
    ] = None  #: optionally, CID specifying the specific version of 'uri' resource this label applies to.
    neg: t.Optional[bool] = None  #: if true, this is a negation label, overwriting a previous label.

    _type: str = 'com.atproto.label.defs#label'
