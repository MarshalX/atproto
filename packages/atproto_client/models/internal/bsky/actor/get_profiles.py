#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`internal.bsky.actor.getProfiles`."""

    dids: t.List[string_formats.Did] = Field(max_length=200)  #: Dids.
    include_takedowns: t.Optional[bool] = (
        False  #: Include taken-down accounts in the response rather than omitting them. For service-to-service moderation use only.
    )
    social_proof: te.Annotated[t.Optional[t.List[string_formats.Did]], Field(max_length=200)] = (
        None  #: DIDs to hydrate social proof (known followers) for. DIDs not also present in `dids` are ignored.
    )


class ParamsDict(t.TypedDict):
    dids: t.List[string_formats.Did]  #: Dids.
    include_takedowns: te.NotRequired[
        t.Optional[bool]
    ]  #: Include taken-down accounts in the response rather than omitting them. For service-to-service moderation use only.
    social_proof: te.NotRequired[
        t.Optional[t.List[string_formats.Did]]
    ]  #: DIDs to hydrate social proof (known followers) for. DIDs not also present in `dids` are ignored.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`internal.bsky.actor.getProfiles`."""

    profiles: t.List['models.AppBskyActorDefs.ProfileViewDetailed']  #: Profiles.
