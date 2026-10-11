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


class Color(base.ModelBase):
    """Definition model for :obj:`place.stream.chat.profile`. Customizations for the color of a user's name in chat."""

    blue: int = Field(ge=0, le=255)  #: Blue.
    green: int = Field(ge=0, le=255)  #: Green.
    red: int = Field(ge=0, le=255)  #: Red.

    py_type: t.Literal['place.stream.chat.profile#color'] = Field(
        default='place.stream.chat.profile#color', alias='$type', frozen=True
    )


SelfLabel = t.Union[t.Literal['bot'], str]  #: Label that a user can apply to their own profile.


class BadgeSelections(base.ModelBase):
    """Definition model for :obj:`place.stream.chat.profile`. Selected badges for display in chat, organized by slot."""

    global_: t.Optional['models.ComAtprotoRepoStrongRef.Main'] = (
        None  #: Selected globally-issued badge (e.g. event badge).
    )
    streamer: te.Annotated[
        t.Optional[t.List['models.PlaceStreamChatProfile.StreamerBadgeSelection']], Field(max_length=20)
    ] = None  #: Selected streamer-issued badges, one per streamer channel.

    py_type: t.Literal['place.stream.chat.profile#badgeSelections'] = Field(
        default='place.stream.chat.profile#badgeSelections', alias='$type', frozen=True
    )


class StreamerBadgeSelection(base.ModelBase):
    """Definition model for :obj:`place.stream.chat.profile`. A selected badge for a specific streamer's channel."""

    badge: (
        'models.ComAtprotoRepoStrongRef.Main'  #: Strong reference to the selected place.stream.badge.issuance record.
    )
    streamer: string_formats.Did  #: DID of the streamer whose channel this selection applies to.

    py_type: t.Literal['place.stream.chat.profile#streamerBadgeSelection'] = Field(
        default='place.stream.chat.profile#streamerBadgeSelection', alias='$type', frozen=True
    )


class Record(base.RecordModelBase):
    """Record model for :obj:`place.stream.chat.profile`."""

    badges: t.Optional['models.PlaceStreamChatProfile.BadgeSelections'] = None  #: Badge selections for display in chat.
    color: t.Optional['models.PlaceStreamChatProfile.Color'] = None  #: Color.
    self_labels: te.Annotated[t.Optional[t.List['models.PlaceStreamChatProfile.SelfLabel']], Field(max_length=10)] = (
        None  #: Self-applied labels for this profile, e.g. 'bot'.
    )

    py_type: t.Literal['place.stream.chat.profile'] = Field(
        default='place.stream.chat.profile', alias='$type', frozen=True
    )


class GetRecordResponse(base.SugarResponseModelBase):
    """Get record response for :obj:`models.PlaceStreamChatProfile.Record`."""

    uri: str  #: The URI of the record.
    value: 'models.PlaceStreamChatProfile.Record'  #: The record.
    cid: t.Optional[str] = None  #: The CID of the record.


class ListRecordsResponse(base.SugarResponseModelBase):
    """List records response for :obj:`models.PlaceStreamChatProfile.Record`."""

    records: t.Dict[str, 'models.PlaceStreamChatProfile.Record']  #: Map of URIs to records.
    cursor: t.Optional[str] = None  #: Next page cursor.


class CreateRecordResponse(base.SugarResponseModelBase):
    """Create record response for :obj:`models.PlaceStreamChatProfile.Record`."""

    uri: str  #: The URI of the record.
    cid: str  #: The CID of the record.
