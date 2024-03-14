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
    from atproto_client.models.unknown_type import UnknownType
from atproto_client.models import base


class StatusAttr(base.ModelBase):
    """Definition model for :obj:`com.atproto.admin.defs`."""

    applied: bool  #: Applied.
    ref: t.Optional[str] = None  #: Ref.

    py_type: te.Literal['com.atproto.admin.defs#statusAttr'] = Field(
        default='com.atproto.admin.defs#statusAttr', alias='$type', frozen=True
    )


class AccountView(base.ModelBase):
    """Definition model for :obj:`com.atproto.admin.defs`."""

    did: str  #: Did.
    handle: str  #: Handle.
    indexed_at: str  #: Indexed at.
    email: t.Optional[str] = None  #: Email.
    email_confirmed_at: t.Optional[str] = None  #: Email confirmed at.
    invite_note: t.Optional[str] = None  #: Invite note.
    invited_by: t.Optional['models.ComAtprotoServerDefs.InviteCode'] = None  #: Invited by.
    invites: t.Optional[t.List['models.ComAtprotoServerDefs.InviteCode']] = None  #: Invites.
    invites_disabled: t.Optional[bool] = None  #: Invites disabled.
    related_records: t.Optional[t.List['UnknownType']] = None  #: Related records.

    py_type: te.Literal['com.atproto.admin.defs#accountView'] = Field(
        default='com.atproto.admin.defs#accountView', alias='$type', frozen=True
    )


class RepoRef(base.ModelBase):
    """Definition model for :obj:`com.atproto.admin.defs`."""

    did: str  #: Did.

    py_type: te.Literal['com.atproto.admin.defs#repoRef'] = Field(
        default='com.atproto.admin.defs#repoRef', alias='$type', frozen=True
    )


class RepoBlobRef(base.ModelBase):
    """Definition model for :obj:`com.atproto.admin.defs`."""

    cid: str  #: Cid.
    did: str  #: Did.
    record_uri: t.Optional[str] = None  #: Record uri.

    py_type: te.Literal['com.atproto.admin.defs#repoBlobRef'] = Field(
        default='com.atproto.admin.defs#repoBlobRef', alias='$type', frozen=True
    )
