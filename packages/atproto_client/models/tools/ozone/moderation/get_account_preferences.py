#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`tools.ozone.moderation.getAccountPreferences`."""

    did: string_formats.Did  #: Did.


class ParamsDict(t.TypedDict):
    did: string_formats.Did  #: Did.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.moderation.getAccountPreferences`."""

    preferences: 'models.AppBskyActorDefs.Preferences'  #: Preferences.
