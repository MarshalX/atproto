#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`tools.ozone.inbox.listNotifications`."""

    cursor: t.Optional[str] = None  #: Cursor.
    did: t.Optional[string_formats.Did] = (
        None  #: Account to preview. Only Ozone staff can read another account; this does not change its read state.
    )
    limit: te.Annotated[t.Optional[int], Field(ge=1, le=100)] = None  #: Limit.
    reasons: t.Optional[
        t.List[
            t.Union[
                t.Literal[
                    'reportResolved',
                    'reportReopened',
                    'actionTaken',
                    'actionReversed',
                    'appealResolved',
                    'standingChanged',
                ],
                str,
            ]
        ]
    ] = None  #: Reasons.
    section: t.Optional[t.Union[t.Literal['reports', 'subjects', 'accountStatus'], str]] = None  #: Section.
    unread_only: t.Optional[bool] = False  #: Unread only.


class ParamsDict(t.TypedDict):
    cursor: te.NotRequired[t.Optional[str]]  #: Cursor.
    did: te.NotRequired[
        t.Optional[string_formats.Did]
    ]  #: Account to preview. Only Ozone staff can read another account; this does not change its read state.
    limit: te.NotRequired[t.Optional[int]]  #: Limit.
    reasons: te.NotRequired[
        t.Optional[
            t.List[
                t.Union[
                    t.Literal[
                        'reportResolved',
                        'reportReopened',
                        'actionTaken',
                        'actionReversed',
                        'appealResolved',
                        'standingChanged',
                    ],
                    str,
                ]
            ]
        ]
    ]  #: Reasons.
    section: te.NotRequired[t.Optional[t.Union[t.Literal['reports', 'subjects', 'accountStatus'], str]]]  #: Section.
    unread_only: te.NotRequired[t.Optional[bool]]  #: Unread only.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.inbox.listNotifications`."""

    notifications: t.List['models.ToolsOzoneInboxDefs.Notification']  #: Notifications.
    cursor: t.Optional[str] = None  #: Cursor.
