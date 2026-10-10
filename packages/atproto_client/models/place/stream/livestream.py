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
    from atproto_client.models.blob_ref import BlobRef
    from atproto_client.models.unknown_type import UnknownType
from atproto_client.models import base, unknown_union


class ViewerCount(base.ModelBase):
    """Definition model for :obj:`place.stream.livestream`."""

    count: int  #: Count.

    py_type: t.Literal['place.stream.livestream#viewerCount'] = Field(
        default='place.stream.livestream#viewerCount', alias='$type', frozen=True
    )


class LivestreamView(base.ModelBase):
    """Definition model for :obj:`place.stream.livestream`."""

    author: 'models.AppBskyActorDefs.ProfileViewBasic'  #: Author.
    cid: string_formats.Cid  #: Cid.
    indexed_at: string_formats.DateTime  #: Indexed at.
    record: 'UnknownType'  #: Record.
    uri: string_formats.AtUri  #: Uri.
    viewer_count: t.Optional['models.PlaceStreamLivestream.ViewerCount'] = (
        None  #: The number of viewers watching this livestream. Use when you can't reasonably use #viewerCount directly.
    )

    py_type: t.Literal['place.stream.livestream#livestreamView'] = Field(
        default='place.stream.livestream#livestreamView', alias='$type', frozen=True
    )


class TeleportArrival(base.ModelBase):
    """Definition model for :obj:`place.stream.livestream`."""

    source: 'models.AppBskyActorDefs.ProfileViewBasic'  #: The streamer who is teleporting their viewers here.
    starts_at: string_formats.DateTime  #: When this teleport started.
    teleport_uri: string_formats.AtUri  #: The URI of the teleport record.
    viewer_count: int  #: How many viewers are arriving from this teleport.
    chat_profile: t.Optional['models.PlaceStreamChatProfile.Record'] = None  #: The chat profile of the source streamer.

    py_type: t.Literal['place.stream.livestream#teleportArrival'] = Field(
        default='place.stream.livestream#teleportArrival', alias='$type', frozen=True
    )


class TeleportCanceled(base.ModelBase):
    """Definition model for :obj:`place.stream.livestream`."""

    reason: t.Literal['deleted', 'denied', 'expired']  #: Why this teleport was canceled.
    teleport_uri: string_formats.AtUri  #: The URI of the teleport record that was canceled.

    py_type: t.Literal['place.stream.livestream#teleportCanceled'] = Field(
        default='place.stream.livestream#teleportCanceled', alias='$type', frozen=True
    )


class StreamplaceAnything(base.ModelBase):
    """Definition model for :obj:`place.stream.livestream`."""

    livestream: unknown_union.OpenUnion[
        t.Union[
            'models.PlaceStreamLivestream.LivestreamView',
            'models.PlaceStreamLivestream.ViewerCount',
            'models.PlaceStreamLivestream.TeleportArrival',
            'models.PlaceStreamLivestream.TeleportCanceled',
            'models.PlaceStreamDefs.BlockView',
            'models.PlaceStreamDefs.Renditions',
            'models.PlaceStreamDefs.Rendition',
            'models.PlaceStreamChatDefs.MessageView',
            'models.PlaceStreamChatDefs.PinnedRecordView',
        ]
    ]  #: Livestream.

    py_type: t.Literal['place.stream.livestream#streamplaceAnything'] = Field(
        default='place.stream.livestream#streamplaceAnything', alias='$type', frozen=True
    )


class NotificationSettings(base.ModelBase):
    """Definition model for :obj:`place.stream.livestream`."""

    push_notification: t.Optional[bool] = (
        None  #: Whether this livestream should trigger a push notification to followers.
    )

    py_type: t.Literal['place.stream.livestream#notificationSettings'] = Field(
        default='place.stream.livestream#notificationSettings', alias='$type', frozen=True
    )


class Record(base.RecordModelBase):
    """Record model for :obj:`place.stream.livestream`."""

    created_at: string_formats.DateTime  #: Client-declared timestamp when this livestream started.
    title: str = Field(max_length=1400)  #: The title of the livestream, as it will be announced to followers.
    activity: t.Optional[
        unknown_union.OpenUnion[t.Union['models.PlaceStreamDefs.ActivityGame', 'models.PlaceStreamDefs.ActivityLabel']]
    ] = None  #: The game or activity being streamed.
    agent: t.Optional[str] = (
        None  #: The source of the livestream, if available, in a User Agent format: `<product> / <product-version> <comment>` e.g. Streamplace/0.7.5 iOS.
    )
    canonical_url: t.Optional[string_formats.Uri] = (
        None  #: The primary URL where this livestream can be viewed, if available.
    )
    ended_at: t.Optional[string_formats.DateTime] = (
        None  #: Client-declared timestamp when this livestream ended. Ended livestreams are not supposed to start up again.
    )
    idle_timeout_seconds: t.Optional[int] = (
        None  #: Time in seconds after which this livestream should be automatically ended if idle. Zero means no timeout.
    )
    last_seen_at: t.Optional[string_formats.DateTime] = (
        None  #: Client-declared timestamp when this livestream was last seen by the Streamplace station.
    )
    notification_settings: t.Optional['models.PlaceStreamLivestream.NotificationSettings'] = (
        None  #: Notification settings.
    )
    post: t.Optional['models.ComAtprotoRepoStrongRef.Main'] = None  #: The post that announced this livestream.
    tags: te.Annotated[t.Optional[t.List[te.Annotated[str, Field(max_length=640)]]], Field(max_length=10)] = (
        None  #: Freeform tags for this stream. Each tag must be alphanumeric (a-z, A-Z, 0-9) plus colon. Tags with colons indicate a specific tag group (e.g. 'lang:en' indicates the stream's primary language).
    )
    thumb: t.Optional['BlobRef'] = None  #: Thumb.
    url: t.Optional[string_formats.Uri] = (
        None  #: The URL where this stream can be found. This is primarily a hint for other Streamplace nodes to locate and replicate the stream.
    )

    py_type: t.Literal['place.stream.livestream'] = Field(default='place.stream.livestream', alias='$type', frozen=True)


class GetRecordResponse(base.SugarResponseModelBase):
    """Get record response for :obj:`models.PlaceStreamLivestream.Record`."""

    uri: str  #: The URI of the record.
    value: 'models.PlaceStreamLivestream.Record'  #: The record.
    cid: t.Optional[str] = None  #: The CID of the record.


class ListRecordsResponse(base.SugarResponseModelBase):
    """List records response for :obj:`models.PlaceStreamLivestream.Record`."""

    records: t.Dict[str, 'models.PlaceStreamLivestream.Record']  #: Map of URIs to records.
    cursor: t.Optional[str] = None  #: Next page cursor.


class CreateRecordResponse(base.SugarResponseModelBase):
    """Create record response for :obj:`models.PlaceStreamLivestream.Record`."""

    uri: str  #: The URI of the record.
    cid: str  #: The CID of the record.
