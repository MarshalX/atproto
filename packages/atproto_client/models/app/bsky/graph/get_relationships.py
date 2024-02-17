##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`app.bsky.graph.getRelationships`."""

    actor: str  #: Primary account requesting relationships for.
    others: t.Optional[t.List[str]] = Field(
        default=None, max_length=30
    )  #: List of 'other' accounts to be related back to the primary.


class ParamsDict(te.TypedDict):
    actor: str  #: Primary account requesting relationships for.
    others: te.NotRequired[t.Optional[t.List[str]]]  #: List of 'other' accounts to be related back to the primary.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`app.bsky.graph.getRelationships`."""

    relationships: t.List[
        te.Annotated[
            t.Union['models.AppBskyGraphDefs.Relationship', 'models.AppBskyGraphDefs.NotFoundActor'],
            Field(discriminator='py_type'),
        ]
    ]  #: Relationships.
    actor: t.Optional[str] = None  #: Actor.
