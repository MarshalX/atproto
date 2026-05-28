#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te

from atproto_client.models import base, string_formats


class Data(base.DataModelBase):
    """Input data model for :obj:`tools.ozone.report.assignModerator`."""

    report_id: int  #: The ID of the report to assign.
    did: t.Optional[string_formats.Did] = (
        None  #: DID to be assigned. Defaults to the caller's DID. Admins may assign to any moderator.
    )
    is_permanent: t.Optional[bool] = (
        None  #: When true, the assignment has no expiry (endAt is null). Throws AlreadyAssigned if another user already has a permanent assignment on this report.
    )
    queue_id: t.Optional[int] = (
        None  #: Optional queue ID to associate the assignment with. If not provided and the report has been assigned on a queue before, it will stay on that queue.
    )


class DataDict(t.TypedDict):
    report_id: int  #: The ID of the report to assign.
    did: te.NotRequired[
        t.Optional[string_formats.Did]
    ]  #: DID to be assigned. Defaults to the caller's DID. Admins may assign to any moderator.
    is_permanent: te.NotRequired[
        t.Optional[bool]
    ]  #: When true, the assignment has no expiry (endAt is null). Throws AlreadyAssigned if another user already has a permanent assignment on this report.
    queue_id: te.NotRequired[
        t.Optional[int]
    ]  #: Optional queue ID to associate the assignment with. If not provided and the report has been assigned on a queue before, it will stay on that queue.
