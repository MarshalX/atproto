##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


class Label(base.ModelBase):

    """Definition model for :obj:`com.atproto.label.defs`. Metadata tag on an atproto resource (eg, repo or record)."""

    cts: str  #: Timestamp when this label was created.
    src: str  #: DID of the actor who created this label.
    uri: str  #: AT URI of the record, repository (account), or other resource that this label applies to.
    val: str = Field(max_length=128)  #: The short string name of the value or type of this label.
    cid: t.Optional[
        str
    ] = None  #: Optionally, CID specifying the specific version of 'uri' resource this label applies to.
    neg: t.Optional[bool] = None  #: If true, this is a negation label, overwriting a previous label.

    py_type: te.Literal['com.atproto.label.defs#label'] = Field(
        default='com.atproto.label.defs#label', alias='$type', frozen=True
    )


class SelfLabels(base.ModelBase):

    """Definition model for :obj:`com.atproto.label.defs`. Metadata tags on an atproto record, published by the author within the record."""

    values: t.List['models.ComAtprotoLabelDefs.SelfLabel'] = Field(max_length=10)  #: Values.

    py_type: te.Literal['com.atproto.label.defs#selfLabels'] = Field(
        default='com.atproto.label.defs#selfLabels', alias='$type', frozen=True
    )


class SelfLabel(base.ModelBase):

    """Definition model for :obj:`com.atproto.label.defs`. Metadata tag on an atproto record, published by the author within the record. Note that schemas should use #selfLabels, not #selfLabel."""

    val: str = Field(max_length=128)  #: The short string name of the value or type of this label.

    py_type: te.Literal['com.atproto.label.defs#selfLabel'] = Field(
        default='com.atproto.label.defs#selfLabel', alias='$type', frozen=True
    )
