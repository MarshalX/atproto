##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Data(base.DataModelBase):
    """Input data model for :obj:`tools.ozone.moderation.emitEvent`."""

    created_by: str  #: Created by.
    event: te.Annotated[
        t.Union[
            'models.ToolsOzoneModerationDefs.ModEventTakedown',
            'models.ToolsOzoneModerationDefs.ModEventAcknowledge',
            'models.ToolsOzoneModerationDefs.ModEventEscalate',
            'models.ToolsOzoneModerationDefs.ModEventComment',
            'models.ToolsOzoneModerationDefs.ModEventLabel',
            'models.ToolsOzoneModerationDefs.ModEventReport',
            'models.ToolsOzoneModerationDefs.ModEventMute',
            'models.ToolsOzoneModerationDefs.ModEventReverseTakedown',
            'models.ToolsOzoneModerationDefs.ModEventUnmute',
            'models.ToolsOzoneModerationDefs.ModEventEmail',
            'models.ToolsOzoneModerationDefs.ModEventTag',
        ],
        Field(discriminator='py_type'),
    ]  #: Event.
    subject: te.Annotated[
        t.Union['models.ComAtprotoAdminDefs.RepoRef', 'models.ComAtprotoRepoStrongRef.Main'],
        Field(discriminator='py_type'),
    ]  #: Subject.
    subject_blob_cids: t.Optional[t.List[str]] = None  #: Subject blob cids.


class DataDict(te.TypedDict):
    created_by: str  #: Created by.
    event: te.Annotated[
        t.Union[
            'models.ToolsOzoneModerationDefs.ModEventTakedown',
            'models.ToolsOzoneModerationDefs.ModEventAcknowledge',
            'models.ToolsOzoneModerationDefs.ModEventEscalate',
            'models.ToolsOzoneModerationDefs.ModEventComment',
            'models.ToolsOzoneModerationDefs.ModEventLabel',
            'models.ToolsOzoneModerationDefs.ModEventReport',
            'models.ToolsOzoneModerationDefs.ModEventMute',
            'models.ToolsOzoneModerationDefs.ModEventReverseTakedown',
            'models.ToolsOzoneModerationDefs.ModEventUnmute',
            'models.ToolsOzoneModerationDefs.ModEventEmail',
            'models.ToolsOzoneModerationDefs.ModEventTag',
        ],
        Field(discriminator='py_type'),
    ]  #: Event.
    subject: te.Annotated[
        t.Union['models.ComAtprotoAdminDefs.RepoRef', 'models.ComAtprotoRepoStrongRef.Main'],
        Field(discriminator='py_type'),
    ]  #: Subject.
    subject_blob_cids: te.NotRequired[t.Optional[t.List[str]]]  #: Subject blob cids.
