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
    """Parameters model for :obj:`com.atproto.space.getLatestCommit`."""

    repo: string_formats.Did  #: Repo.
    space: string_formats.SpaceRef  #: Space.


class ParamsDict(t.TypedDict):
    repo: string_formats.Did  #: Repo.
    space: string_formats.SpaceRef  #: Space.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`com.atproto.space.getLatestCommit`."""

    commit: 'models.ComAtprotoSpaceDefs.Commit'  #: Commit.
