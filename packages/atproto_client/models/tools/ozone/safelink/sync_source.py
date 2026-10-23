#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

from pydantic import Field

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Data(base.DataModelBase):
    """Input data model for :obj:`tools.ozone.safelink.syncSource`."""

    rules: t.List['models.ToolsOzoneSafelinkSyncSource.SourceRule']  #: Rules.
    source: str = Field(max_length=128)  #: Source whose rules are being synchronized.


class DataDict(t.TypedDict):
    rules: t.List['models.ToolsOzoneSafelinkSyncSource.SourceRule']  #: Rules.
    source: str  #: Source whose rules are being synchronized.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.safelink.syncSource`."""

    added: int  #: Added.
    events: int  #: Events.
    removed: int  #: Removed.
    updated: int  #: Updated.


class SourceRule(base.ModelBase):
    """Definition model for :obj:`tools.ozone.safelink.syncSource`."""

    action: 'models.ToolsOzoneSafelinkDefs.ActionType'  #: Action.
    pattern: 'models.ToolsOzoneSafelinkDefs.PatternType'  #: Pattern.
    reason: 'models.ToolsOzoneSafelinkDefs.ReasonType'  #: Reason.
    url: str  #: Url.

    py_type: t.Literal['tools.ozone.safelink.syncSource#sourceRule'] = Field(
        default='tools.ozone.safelink.syncSource#sourceRule', alias='$type', frozen=True
    )
