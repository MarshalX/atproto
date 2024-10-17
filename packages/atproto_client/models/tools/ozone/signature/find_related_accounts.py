##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`tools.ozone.signature.findRelatedAccounts`."""

    did: str  #: Did.
    cursor: t.Optional[str] = None  #: Cursor.
    limit: t.Optional[int] = Field(default=50, ge=1, le=100)  #: Limit.


class ParamsDict(t.TypedDict):
    did: str  #: Did.
    cursor: te.NotRequired[t.Optional[str]]  #: Cursor.
    limit: te.NotRequired[t.Optional[int]]  #: Limit.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.signature.findRelatedAccounts`."""

    accounts: t.List['models.ToolsOzoneSignatureFindRelatedAccounts.RelatedAccount']  #: Accounts.
    cursor: t.Optional[str] = None  #: Cursor.


class RelatedAccount(base.ModelBase):
    """Definition model for :obj:`tools.ozone.signature.findRelatedAccounts`."""

    account: 'models.ComAtprotoAdminDefs.AccountView'  #: Account.
    similarities: t.Optional[t.List['models.ToolsOzoneSignatureDefs.SigDetail']] = None  #: Similarities.

    py_type: t.Literal['tools.ozone.signature.findRelatedAccounts#relatedAccount'] = Field(
        default='tools.ozone.signature.findRelatedAccounts#relatedAccount', alias='$type', frozen=True
    )
