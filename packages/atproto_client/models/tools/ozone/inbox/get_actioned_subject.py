#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

from atproto_client.models import base, string_formats


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`tools.ozone.inbox.getActionedSubject`."""

    subject: string_formats.Uri  #: DID or AT-URI of the subject to retrieve.
    cursor: t.Optional[str] = None  #: Opaque cursor for the next page of this subject's action history.
    did: t.Optional[string_formats.Did] = (
        None  #: Account to preview. Defaults to the authenticated account; another account requires an active moderator, triage, or admin credential.
    )
    limit: te.Annotated[t.Optional[int], Field(ge=1, le=100)] = None  #: Maximum number of actions to return.


class ParamsDict(t.TypedDict):
    subject: string_formats.Uri  #: DID or AT-URI of the subject to retrieve.
    cursor: te.NotRequired[t.Optional[str]]  #: Opaque cursor for the next page of this subject's action history.
    did: te.NotRequired[
        t.Optional[string_formats.Did]
    ]  #: Account to preview. Defaults to the authenticated account; another account requires an active moderator, triage, or admin credential.
    limit: te.NotRequired[t.Optional[int]]  #: Maximum number of actions to return.
