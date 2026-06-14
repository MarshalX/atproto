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
    social_proof: te.Annotated[t.Optional[t.List[string_formats.Did]], Field(max_length=200)] = (
        None  #: DIDs to hydrate social proof (known followers) for. DIDs not also present in `dids` are ignored.
    )
    viewer: t.Optional[string_formats.Did] = (
        None  #: DID of the account on whose behalf the request is made (not included for public/unauthenticated requests). Used for viewer-relative state, including social proof.
    )


class ParamsDict(t.TypedDict):
    dids: t.List[string_formats.Did]  #: Dids.
    social_proof: te.NotRequired[
        t.Optional[t.List[string_formats.Did]]
    ]  #: DIDs to hydrate social proof (known followers) for. DIDs not also present in `dids` are ignored.
    viewer: te.NotRequired[
        t.Optional[string_formats.Did]
    ]  #: DID of the account on whose behalf the request is made (not included for public/unauthenticated requests). Used for viewer-relative state, including social proof.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`internal.bsky.actor.getProfiles`."""

    profiles: t.List['models.AppBskyActorDefs.ProfileViewDetailed']  #: Profiles.
