##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te

from atproto_client.models import base


class Data(base.DataModelBase):
    """Input data model for :obj:`tools.ozone.report.refreshStats`."""

    end_date: str  #: End date for recomputation, inclusive (YYYY-MM-DD).
    start_date: str  #: Start date for recomputation, inclusive (YYYY-MM-DD).
    queue_ids: t.Optional[t.List[int]] = None  #: Optional list of queue IDs to recompute. Omit to recompute all groups.


class DataDict(t.TypedDict):
    end_date: str  #: End date for recomputation, inclusive (YYYY-MM-DD).
    start_date: str  #: Start date for recomputation, inclusive (YYYY-MM-DD).
    queue_ids: te.NotRequired[
        t.Optional[t.List[int]]
    ]  #: Optional list of queue IDs to recompute. Omit to recompute all groups.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.report.refreshStats`."""
