##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

from atproto_client.models import base, string_formats


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`com.atproto.sync.getRepoStatus`."""

    did: string_formats.Did  #: The DID of the repo.


class ParamsDict(t.TypedDict):
    did: string_formats.Did  #: The DID of the repo.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`com.atproto.sync.getRepoStatus`."""

    active: bool  #: Active.
    did: string_formats.Did  #: Did.
    rev: t.Optional[str] = None  #: Optional field, the current rev of the repo, if active=true.
    status: t.Optional[t.Union[t.Literal['takendown'], t.Literal['suspended'], t.Literal['deactivated'], str]] = (
        None  #: If active=false, this optional field indicates a possible reason for why the account is not active. If active=false and no status is supplied, then the host makes no claim for why the repository is no longer being hosted.
    )
