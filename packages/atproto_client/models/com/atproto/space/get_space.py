#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base, unknown_union


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`com.atproto.space.getSpace`."""

    space: string_formats.SpaceRef  #: Space.


class ParamsDict(t.TypedDict):
    space: string_formats.SpaceRef  #: Space.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`com.atproto.space.getSpace`."""

    policy: unknown_union.OpenUnion[
        t.Union[
            'models.ComAtprotoPersonalspacePolicy.Main',
            'models.ComAtprotoMemberspacePolicy.Main',
            'models.ComAtprotoManagedspacePolicy.Main',
        ]
    ]  #: PDSes must support all of the listed policies. Other space hosts may support only some of them, and any host may support policies beyond those listed.
    space: string_formats.SpaceRef  #: Space.
