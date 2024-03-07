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


class LabelerView(base.ModelBase):
    """Definition model for :obj:`app.bsky.labeler.defs`."""

    cid: str  #: Cid.
    creator: 'models.AppBskyActorDefs.ProfileView'  #: Creator.
    indexed_at: str  #: Indexed at.
    uri: str  #: Uri.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.
    like_count: t.Optional[int] = Field(default=None, ge=0)  #: Like count.
    viewer: t.Optional['models.AppBskyLabelerDefs.LabelerViewerState'] = None  #: Viewer.

    py_type: te.Literal['app.bsky.labeler.defs#labelerView'] = Field(
        default='app.bsky.labeler.defs#labelerView', alias='$type', frozen=True
    )


class LabelerViewDetailed(base.ModelBase):
    """Definition model for :obj:`app.bsky.labeler.defs`."""

    cid: str  #: Cid.
    creator: 'models.AppBskyActorDefs.ProfileView'  #: Creator.
    indexed_at: str  #: Indexed at.
    policies: 'models.AppBskyLabelerDefs.LabelerPolicies'  #: Policies.
    uri: str  #: Uri.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.
    like_count: t.Optional[int] = Field(default=None, ge=0)  #: Like count.
    viewer: t.Optional['models.AppBskyLabelerDefs.LabelerViewerState'] = None  #: Viewer.

    py_type: te.Literal['app.bsky.labeler.defs#labelerViewDetailed'] = Field(
        default='app.bsky.labeler.defs#labelerViewDetailed', alias='$type', frozen=True
    )


class LabelerViewerState(base.ModelBase):
    """Definition model for :obj:`app.bsky.labeler.defs`."""

    like: t.Optional[str] = None  #: Like.

    py_type: te.Literal['app.bsky.labeler.defs#labelerViewerState'] = Field(
        default='app.bsky.labeler.defs#labelerViewerState', alias='$type', frozen=True
    )


class LabelerPolicies(base.ModelBase):
    """Definition model for :obj:`app.bsky.labeler.defs`."""

    label_values: t.List[
        'models.ComAtprotoLabelDefs.LabelValue'
    ]  #: The label values which this labeler publishes. May include global or custom labels.
    label_value_definitions: t.Optional[
        t.List['models.ComAtprotoLabelDefs.LabelValueDefinition']
    ] = None  #: Label values created by this labeler and scoped exclusively to it. Labels defined here will override global label definitions for this labeler.

    py_type: te.Literal['app.bsky.labeler.defs#labelerPolicies'] = Field(
        default='app.bsky.labeler.defs#labelerPolicies', alias='$type', frozen=True
    )
