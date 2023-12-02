##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


class Data(base.DataModelBase):

    """Input data model for :obj:`com.atproto.admin.emitModerationEvent`."""

    created_by: str = Field(alias='createdBy')  #: Created by.
    event: te.Annotated[
        t.Union[
            'models.ComAtprotoAdminDefs.ModEventTakedown',
            'models.ComAtprotoAdminDefs.ModEventAcknowledge',
            'models.ComAtprotoAdminDefs.ModEventEscalate',
            'models.ComAtprotoAdminDefs.ModEventComment',
            'models.ComAtprotoAdminDefs.ModEventLabel',
            'models.ComAtprotoAdminDefs.ModEventReport',
            'models.ComAtprotoAdminDefs.ModEventMute',
            'models.ComAtprotoAdminDefs.ModEventReverseTakedown',
            'models.ComAtprotoAdminDefs.ModEventUnmute',
            'models.ComAtprotoAdminDefs.ModEventEmail',
        ],
        Field(discriminator='py_type'),
    ]  #: Event.
    subject: te.Annotated[
        t.Union['models.ComAtprotoAdminDefs.RepoRef', 'models.ComAtprotoRepoStrongRef.Main'],
        Field(discriminator='py_type'),
    ]  #: Subject.
    subject_blob_cids: t.Optional[t.List[str]] = Field(default=None, alias='subjectBlobCids')  #: Subject blob cids.


class DataDict(te.TypedDict):
    created_by: str  #: Created by.
    event: te.Annotated[
        t.Union[
            'models.ComAtprotoAdminDefs.ModEventTakedown',
            'models.ComAtprotoAdminDefs.ModEventAcknowledge',
            'models.ComAtprotoAdminDefs.ModEventEscalate',
            'models.ComAtprotoAdminDefs.ModEventComment',
            'models.ComAtprotoAdminDefs.ModEventLabel',
            'models.ComAtprotoAdminDefs.ModEventReport',
            'models.ComAtprotoAdminDefs.ModEventMute',
            'models.ComAtprotoAdminDefs.ModEventReverseTakedown',
            'models.ComAtprotoAdminDefs.ModEventUnmute',
            'models.ComAtprotoAdminDefs.ModEventEmail',
        ],
        Field(discriminator='py_type'),
    ]  #: Event.
    subject: te.Annotated[
        t.Union['models.ComAtprotoAdminDefs.RepoRef', 'models.ComAtprotoRepoStrongRef.Main'],
        Field(discriminator='py_type'),
    ]  #: Subject.
    subject_blob_cids: te.NotRequired[t.Optional[t.List[str]]]  #: Subject blob cids.
