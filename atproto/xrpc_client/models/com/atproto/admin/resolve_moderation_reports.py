##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

from pydantic import Field

if t.TYPE_CHECKING:
    pass
from atproto.xrpc_client.models import base


class Data(base.DataModelBase):

    """Input data model for :obj:`com.atproto.admin.resolveModerationReports`."""

    action_id: int = Field(alias='actionId')  #: Action id.
    created_by: str = Field(alias='createdBy')  #: Created by.
    report_ids: t.List[int] = Field(alias='reportIds')  #: Report ids.
