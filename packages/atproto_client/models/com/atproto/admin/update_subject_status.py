#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base, unknown_union


class Data(base.DataModelBase):
    """Input data model for :obj:`com.atproto.admin.updateSubjectStatus`."""

    subject: unknown_union.OpenUnion[
        t.Union[
            'models.ComAtprotoAdminDefs.RepoRef',
            'models.ComAtprotoRepoStrongRef.Main',
            'models.ComAtprotoAdminDefs.RepoBlobRef',
        ]
    ]  #: Subject.
    deactivated: t.Optional['models.ComAtprotoAdminDefs.StatusAttr'] = None  #: Deactivated.
    takedown: t.Optional['models.ComAtprotoAdminDefs.StatusAttr'] = None  #: Takedown.


class DataDict(t.TypedDict):
    subject: unknown_union.OpenUnion[
        t.Union[
            'models.ComAtprotoAdminDefs.RepoRef',
            'models.ComAtprotoRepoStrongRef.Main',
            'models.ComAtprotoAdminDefs.RepoBlobRef',
        ]
    ]  #: Subject.
    deactivated: te.NotRequired[t.Optional['models.ComAtprotoAdminDefs.StatusAttr']]  #: Deactivated.
    takedown: te.NotRequired[t.Optional['models.ComAtprotoAdminDefs.StatusAttr']]  #: Takedown.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`com.atproto.admin.updateSubjectStatus`."""

    subject: unknown_union.OpenUnion[
        t.Union[
            'models.ComAtprotoAdminDefs.RepoRef',
            'models.ComAtprotoRepoStrongRef.Main',
            'models.ComAtprotoAdminDefs.RepoBlobRef',
        ]
    ]  #: Subject.
    takedown: t.Optional['models.ComAtprotoAdminDefs.StatusAttr'] = None  #: Takedown.
