#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base, unknown_union


class Data(base.DataModelBase):
    """Input data model for :obj:`tools.ozone.inbox.appealActionedSubject`."""

    subject: unknown_union.OpenUnion[
        t.Union['models.ComAtprotoAdminDefs.RepoRef', 'models.ComAtprotoRepoStrongRef.Main']
    ]  #: Subject being appealed.
    action: t.Optional[
        te.Annotated[
            t.Union[
                'models.ToolsOzoneInboxAppealActionedSubject.ActionRef',
                'models.ToolsOzoneInboxAppealActionedSubject.LabelRef',
                'models.ToolsOzoneInboxAppealActionedSubject.TakedownRef',
            ],
            Field(discriminator='py_type'),
        ]
    ] = None  #: Moderation action being appealed.
    mod_tool: t.Optional['models.ComAtprotoModerationCreateReport.ModTool'] = None  #: Mod tool.
    reason: te.Annotated[t.Optional[str], Field(max_length=20000)] = None  #: Optional explanation supplied by the user.


class DataDict(t.TypedDict):
    subject: unknown_union.OpenUnion[
        t.Union['models.ComAtprotoAdminDefs.RepoRef', 'models.ComAtprotoRepoStrongRef.Main']
    ]  #: Subject being appealed.
    action: te.NotRequired[
        t.Optional[
            te.Annotated[
                t.Union[
                    'models.ToolsOzoneInboxAppealActionedSubject.ActionRef',
                    'models.ToolsOzoneInboxAppealActionedSubject.LabelRef',
                    'models.ToolsOzoneInboxAppealActionedSubject.TakedownRef',
                ],
                Field(discriminator='py_type'),
            ]
        ]
    ]  #: Moderation action being appealed.
    mod_tool: te.NotRequired[t.Optional['models.ComAtprotoModerationCreateReport.ModTool']]  #: Mod tool.
    reason: te.NotRequired[t.Optional[str]]  #: Optional explanation supplied by the user.


class ActionRef(base.ModelBase):
    """Definition model for :obj:`tools.ozone.inbox.appealActionedSubject`."""

    id: int = Field(ge=1)  #: ID of the moderation action being appealed, available via actions in mod inbox.

    py_type: t.Literal['tools.ozone.inbox.appealActionedSubject#actionRef'] = Field(
        default='tools.ozone.inbox.appealActionedSubject#actionRef', alias='$type', frozen=True
    )


class LabelRef(base.ModelBase):
    """Definition model for :obj:`tools.ozone.inbox.appealActionedSubject`."""

    val: str = Field(min_length=1)  #: Label being appealed.

    py_type: t.Literal['tools.ozone.inbox.appealActionedSubject#labelRef'] = Field(
        default='tools.ozone.inbox.appealActionedSubject#labelRef', alias='$type', frozen=True
    )


class TakedownRef(base.ModelBase):
    """Definition model for :obj:`tools.ozone.inbox.appealActionedSubject`."""

    py_type: t.Literal['tools.ozone.inbox.appealActionedSubject#takedownRef'] = Field(
        default='tools.ozone.inbox.appealActionedSubject#takedownRef', alias='$type', frozen=True
    )
