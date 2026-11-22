#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base, unknown_union


class Data(base.DataModelBase):
    """Input data model for :obj:`com.atproto.space.createSpace`."""

    policy: unknown_union.OpenUnion[
        t.Union[
            'models.ComAtprotoPersonalspacePolicy.Main',
            'models.ComAtprotoMemberspacePolicy.Main',
            'models.ComAtprotoManagedspacePolicy.Main',
        ]
    ]  #: PDSes must support all of the listed policies. Other space hosts may support only some of them, and any host may support policies beyond those listed.
    space_type: string_formats.Nsid  #: Space type.
    skey: t.Optional[string_formats.RecordKey] = None  #: Space key. Generated as a TID if not provided.


class DataDict(t.TypedDict):
    policy: unknown_union.OpenUnion[
        t.Union[
            'models.ComAtprotoPersonalspacePolicy.Main',
            'models.ComAtprotoMemberspacePolicy.Main',
            'models.ComAtprotoManagedspacePolicy.Main',
        ]
    ]  #: PDSes must support all of the listed policies. Other space hosts may support only some of them, and any host may support policies beyond those listed.
    space_type: string_formats.Nsid  #: Space type.
    skey: te.NotRequired[t.Optional[string_formats.RecordKey]]  #: Space key. Generated as a TID if not provided.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`com.atproto.space.createSpace`."""

    space: string_formats.SpaceRef  #: Space.
