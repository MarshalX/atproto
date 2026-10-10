#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te

from atproto_client.models import base, string_formats


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`tools.ozone.inbox.getAccountStatus`."""

    did: t.Optional[string_formats.Did] = (
        None  #: Account to preview. Only Ozone staff can read another account; this does not change its read state.
    )


class ParamsDict(t.TypedDict):
    did: te.NotRequired[
        t.Optional[string_formats.Did]
    ]  #: Account to preview. Only Ozone staff can read another account; this does not change its read state.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.inbox.getAccountStatus`."""

    src: string_formats.Did  #: DID of the moderation service returning this status.
    standing: t.Union[t.Literal['good', 'warning', 'atRisk'], str]  #: Standing.
    updated_at: string_formats.DateTime  #: Newest account-status update or strike timestamp used to derive this standing, or the Unix epoch when neither exists. This is not a standing-transition timestamp; expiry can change standing without changing this value.
    expires_at: t.Optional[string_formats.DateTime] = (
        None  #: Time at which the current suspension expires. Present only for a temporary suspension.
    )
