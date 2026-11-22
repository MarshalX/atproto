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


class Data(base.DataModelBase):
    """Input data model for :obj:`com.atproto.space.notifySpaceUpdate`."""

    space: string_formats.SpaceRef  #: Space.
    token: str = Field(max_length=512)  #: The token the endpoint was registered with.
    update: unknown_union.OpenUnion[
        t.Union[
            'models.ComAtprotoSpaceDefs.RepoWrite',
            'models.ComAtprotoSpaceDefs.RepoRemoved',
            'models.ComAtprotoSpaceNotifySpaceUpdate.SpaceDeleted',
            'models.ComAtprotoSpaceNotifySpaceUpdate.RegistrationExpired',
        ]
    ]  #: Update.


class DataDict(t.TypedDict):
    space: string_formats.SpaceRef  #: Space.
    token: str  #: The token the endpoint was registered with.
    update: unknown_union.OpenUnion[
        t.Union[
            'models.ComAtprotoSpaceDefs.RepoWrite',
            'models.ComAtprotoSpaceDefs.RepoRemoved',
            'models.ComAtprotoSpaceNotifySpaceUpdate.SpaceDeleted',
            'models.ComAtprotoSpaceNotifySpaceUpdate.RegistrationExpired',
        ]
    ]  #: Update.


class SpaceDeleted(base.ModelBase):
    """Definition model for :obj:`com.atproto.space.notifySpaceUpdate`. The space has been deleted. Confirm with authorizeSpaceSync before dropping its data."""

    py_type: t.Literal['com.atproto.space.notifySpaceUpdate#spaceDeleted'] = Field(
        default='com.atproto.space.notifySpaceUpdate#spaceDeleted', alias='$type', frozen=True
    )


class RegistrationExpired(base.ModelBase):
    """Definition model for :obj:`com.atproto.space.notifySpaceUpdate`. The endpoint's registration has expired. Sent in place of the first update after expiry. Call authorizeSpaceSync to keep receiving notifications."""

    space_rev: string_formats.Tid  #: Space rev.

    py_type: t.Literal['com.atproto.space.notifySpaceUpdate#registrationExpired'] = Field(
        default='com.atproto.space.notifySpaceUpdate#registrationExpired', alias='$type', frozen=True
    )
