#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

from pydantic import Field

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base, unknown_union


class SubjectView(base.ModelBase):
    """Definition model for :obj:`tools.ozone.inbox.defs`. A subject belonging to the viewer that has moderation actions against it."""

    created_at: string_formats.DateTime  #: Created at.
    enforcement: 'models.ToolsOzoneInboxDefs.EnforcementView'  #: Enforcement.
    src: string_formats.Did  #: DID of the moderation service that took the actions.
    subject: unknown_union.OpenUnion[
        t.Union['models.ComAtprotoAdminDefs.RepoRef', 'models.ComAtprotoRepoStrongRef.Main']
    ]  #: Subject.
    updated_at: string_formats.DateTime  #: Updated at.
    action_count: t.Optional[int] = None  #: Action count.
    appeal: t.Optional['models.ToolsOzoneInboxDefs.AppealView'] = None  #: Appeal.
    available_actions: t.Optional[t.List[t.Union[t.Literal['appeal'], str]]] = None  #: Available actions.
    latest_action: t.Optional['models.ToolsOzoneInboxDefs.ActionView'] = None  #: Latest action.

    py_type: t.Literal['tools.ozone.inbox.defs#subjectView'] = Field(
        default='tools.ozone.inbox.defs#subjectView', alias='$type', frozen=True
    )


class EnforcementView(base.ModelBase):
    """Definition model for :obj:`tools.ozone.inbox.defs`. The current enforcement state of a subject."""

    state: t.Union[t.Literal['none', 'labeled', 'removed', 'suspended', 'takendown'], str]  #: State.
    expires_at: t.Optional[string_formats.DateTime] = None  #: Expires at.
    labels: t.Optional[t.List[str]] = None  #: Active label values on the subject, excluding negated and expired labels.
    scope: t.Optional[t.Union[t.Literal['network', 'app', 'labelOnly'], str]] = None  #: Scope.

    py_type: t.Literal['tools.ozone.inbox.defs#enforcementView'] = Field(
        default='tools.ozone.inbox.defs#enforcementView', alias='$type', frozen=True
    )


class AppealView(base.ModelBase):
    """Definition model for :obj:`tools.ozone.inbox.defs`. The state of the viewer's appeal against the actions on a subject."""

    state: t.Union[t.Literal['none', 'pending', 'resolved', 'superseded', 'expired'], str]  #: State.
    appealable_until: t.Optional[string_formats.DateTime] = None  #: Appealable until.
    appealed_at: t.Optional[string_formats.DateTime] = None  #: Appealed at.
    note: t.Optional[str] = (
        None  #: Moderator explanation, from the publicNote on the closing activity. Absent if none was written.
    )
    resolved_at: t.Optional[string_formats.DateTime] = None  #: When the appeal's report was closed.

    py_type: t.Literal['tools.ozone.inbox.defs#appealView'] = Field(
        default='tools.ozone.inbox.defs#appealView', alias='$type', frozen=True
    )


class ActionView(base.ModelBase):
    """Definition model for :obj:`tools.ozone.inbox.defs`. A single moderation action taken against a subject."""

    created_at: string_formats.DateTime  #: Created at.
    id: int  #: Action ID (moderation event ID).
    type: str  #: Public action type.
    expires_at: t.Optional[string_formats.DateTime] = None  #: Expires at.
    labels: t.Optional[t.List[str]] = None  #: Label values, for labelApplied/labelRemoved.
    policies: t.Optional[t.List[str]] = None  #: Policies that were applied in this action.
    reversed_at: t.Optional[string_formats.DateTime] = None  #: Reversed at.
    scope: t.Optional[t.Union[t.Literal['network', 'app', 'labelOnly'], str]] = None  #: Scope.

    py_type: t.Literal['tools.ozone.inbox.defs#actionView'] = Field(
        default='tools.ozone.inbox.defs#actionView', alias='$type', frozen=True
    )
