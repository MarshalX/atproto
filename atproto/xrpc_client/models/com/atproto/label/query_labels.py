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
class Params(base.ParamsModelBase):

    """Parameters model for :obj:`com.atproto.label.queryLabels`.

    Attributes:
        uriPatterns: List of AT URI patterns to match (boolean 'OR'). Each may be a prefix (ending with '*'; will match inclusive of the string leading to '*'), or a full URI.
        sources: Optional list of label sources (DIDs) to filter on.
        limit: Limit.
        cursor: Cursor.
    """

    uriPatterns: List[str]
    cursor: Optional[str] = None
    limit: Optional[int] = None
    sources: Optional[List[str]] = None


@dataclass
class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.label.queryLabels`.

    Attributes:
        cursor: Cursor.
        labels: Labels.
    """

    labels: List['models.ComAtprotoLabelDefs.Label']
    cursor: Optional[str] = None
