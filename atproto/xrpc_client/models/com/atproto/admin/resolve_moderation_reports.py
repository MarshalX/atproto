##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

from atproto.xrpc_client.models import base


class Data(base.DataModelBase):

    """Input data model for :obj:`com.atproto.admin.resolveModerationReports`."""

    action_id: int = Field(alias='actionId')  #: Action id.
    created_by: str = Field(alias='createdBy')  #: Created by.
    report_ids: t.List[int] = Field(alias='reportIds')  #: Report ids.


class DataDict(te.TypedDict):
    action_id: int  #: Action id.
    created_by: str  #: Created by.
    report_ids: t.List[int]  #: Report ids.
