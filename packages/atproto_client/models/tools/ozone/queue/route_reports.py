##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

from atproto_client.models import base


class Data(base.DataModelBase):
    """Input data model for :obj:`tools.ozone.queue.routeReports`."""

    end_report_id: int  #: End of report ID range (inclusive). Difference between start and end must be less than 5,000.
    start_report_id: int  #: Start of report ID range (inclusive).


class DataDict(t.TypedDict):
    end_report_id: int  #: End of report ID range (inclusive). Difference between start and end must be less than 5,000.
    start_report_id: int  #: Start of report ID range (inclusive).


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.queue.routeReports`."""

    assigned: int  #: The number of reports assigned to a queue.
    unmatched: int  #: The number of reports with no matching queue.
