##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`tools.ozone.set.getValues`."""

    name: str  #: Name.
    cursor: t.Optional[str] = None  #: Cursor.
    limit: t.Optional[int] = Field(default=100, ge=1, le=1000)  #: Limit.


class ParamsDict(t.TypedDict):
    name: str  #: Name.
    cursor: te.NotRequired[t.Optional[str]]  #: Cursor.
    limit: te.NotRequired[t.Optional[int]]  #: Limit.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.set.getValues`."""

    set: 'models.ToolsOzoneSetDefs.SetView'  #: Set.
    values: t.List[str]  #: Values.
    cursor: t.Optional[str] = None  #: Cursor.
