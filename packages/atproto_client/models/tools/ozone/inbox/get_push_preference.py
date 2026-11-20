#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

from atproto_client.models import base, string_formats


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`tools.ozone.inbox.getPushPreference`."""

    category: t.Literal['reports', 'account', 'labels']  #: Category.
    recipient_did: string_formats.Did  #: Recipient did.


class ParamsDict(t.TypedDict):
    category: t.Literal['reports', 'account', 'labels']  #: Category.
    recipient_did: string_formats.Did  #: Recipient did.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.inbox.getPushPreference`."""

    enabled: bool  #: Enabled.
