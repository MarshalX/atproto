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


class Params(base.ParamsModelBase):

    """Parameters model for :obj:`com.atproto.admin.getSubjectStatus`."""

    blob: t.Optional[str] = None  #: Blob.
    did: t.Optional[str] = None  #: Did.
    uri: t.Optional[str] = None  #: Uri.


class ParamsDict(te.TypedDict):
    blob: te.NotRequired[t.Optional[str]]  #: Blob.
    did: te.NotRequired[t.Optional[str]]  #: Did.
    uri: te.NotRequired[t.Optional[str]]  #: Uri.


class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.admin.getSubjectStatus`."""

    subject: te.Annotated[
        t.Union[
            'models.ComAtprotoAdminDefs.RepoRef',
            'models.ComAtprotoRepoStrongRef.Main',
            'models.ComAtprotoAdminDefs.RepoBlobRef',
        ],
        Field(discriminator='py_type'),
    ]  #: Subject.
    takedown: t.Optional['models.ComAtprotoAdminDefs.StatusAttr'] = None  #: Takedown.
