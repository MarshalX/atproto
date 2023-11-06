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

    """Input data model for :obj:`com.atproto.admin.updateSubjectStatus`."""

    subject: te.Annotated[
        t.Union[
            'models.ComAtprotoAdminDefs.RepoRef',
            'models.ComAtprotoRepoStrongRef.Main',
            'models.ComAtprotoAdminDefs.RepoBlobRef',
        ],
        Field(discriminator='py_type'),
    ]  #: Subject.
    takedown: t.Optional['models.ComAtprotoAdminDefs.StatusAttr'] = None  #: Takedown.


class DataDict(te.TypedDict):
    subject: te.Annotated[
        t.Union[
            'models.ComAtprotoAdminDefs.RepoRef',
            'models.ComAtprotoRepoStrongRef.Main',
            'models.ComAtprotoAdminDefs.RepoBlobRef',
        ],
        Field(discriminator='py_type'),
    ]  #: Subject.
    takedown: te.NotRequired[t.Optional['models.ComAtprotoAdminDefs.StatusAttr']]  #: Takedown.


class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.admin.updateSubjectStatus`."""

    subject: te.Annotated[
        t.Union[
            'models.ComAtprotoAdminDefs.RepoRef',
            'models.ComAtprotoRepoStrongRef.Main',
            'models.ComAtprotoAdminDefs.RepoBlobRef',
        ],
        Field(discriminator='py_type'),
    ]  #: Subject.
    takedown: t.Optional['models.ComAtprotoAdminDefs.StatusAttr'] = None  #: Takedown.
