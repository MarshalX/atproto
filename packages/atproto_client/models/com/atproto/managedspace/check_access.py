#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te

from atproto_client.models import base, string_formats


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`com.atproto.managedspace.checkAccess`."""

    space: string_formats.SpaceRef  #: Space.
    client_id: t.Optional[string_formats.Uri] = None  #: OAuth client ID of the requesting app, if attested.
    repo: t.Optional[string_formats.Did] = None  #: Repo.


class ParamsDict(t.TypedDict):
    space: string_formats.SpaceRef  #: Space.
    client_id: te.NotRequired[t.Optional[string_formats.Uri]]  #: OAuth client ID of the requesting app, if attested.
    repo: te.NotRequired[t.Optional[string_formats.Did]]  #: Repo.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`com.atproto.managedspace.checkAccess`."""

    read: bool  #: Read.
    write: bool  #: Write.
