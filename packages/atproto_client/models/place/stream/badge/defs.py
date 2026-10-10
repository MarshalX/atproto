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
from atproto_client.models import base

Bot = t.Literal[
    'place.stream.badge.defs#bot'
]  #: This user is a bot. Self-applied via place.stream.chat.profile selfLabels.

Mod = t.Literal['place.stream.badge.defs#mod']  #: This user is a moderator. Displayed with a sword icon.

Vip = t.Literal['place.stream.badge.defs#vip']  #: This user is a very important person.

Event = t.Literal['place.stream.badge.defs#event']  #: This user has won or earned a special event or contest badge.

Streamer = t.Literal['place.stream.badge.defs#streamer']  #: This user is the streamer. Displayed with a star icon.


class BadgeSlot(base.ModelBase):
    """Definition model for :obj:`place.stream.badge.defs`. A display slot containing available issuance-based badges and which one (if any) is currently selected."""

    available: t.List['models.PlaceStreamBadgeDefs.BadgeIssuanceView']  #: All badges available for this slot.
    selected: t.Optional['models.PlaceStreamBadgeDefs.BadgeIssuanceView'] = (
        None  #: The currently selected badge in this slot, if any.
    )

    py_type: t.Literal['place.stream.badge.defs#badgeSlot'] = Field(
        default='place.stream.badge.defs#badgeSlot', alias='$type', frozen=True
    )


class BadgeView(base.ModelBase):
    """Definition model for :obj:`place.stream.badge.defs`. View of a badge record, with fields resolved for display. If the DID in issuer is not the current streamplace node, the signature field shall be required."""

    badge_type: t.Union[
        'models.PlaceStreamBadgeDefs.Mod',
        'models.PlaceStreamBadgeDefs.Streamer',
        'models.PlaceStreamBadgeDefs.Vip',
        'models.PlaceStreamBadgeDefs.Event',
        'models.PlaceStreamBadgeDefs.Bot',
        str,
    ]  #: Badge type.
    issuer: string_formats.Did  #: DID of the badge issuer.
    recipient: string_formats.Did  #: DID of the badge recipient.
    description: t.Optional[str] = None  #: Description from the badge definition.
    image_url: t.Optional[string_formats.Uri] = None  #: Resolved image URL for the badge icon.
    name: t.Optional[str] = None  #: Display name from the badge definition.
    signature: t.Optional[str] = None  #: TODO: Cryptographic signature of the badge (of a place.stream.key).

    py_type: t.Literal['place.stream.badge.defs#badgeView'] = Field(
        default='place.stream.badge.defs#badgeView', alias='$type', frozen=True
    )


class BadgeIssuanceView(base.ModelBase):
    """Definition model for :obj:`place.stream.badge.defs`. A resolved view of a badge issuance, including def fields for display."""

    badge_type: t.Union['models.PlaceStreamBadgeDefs.Vip', 'models.PlaceStreamBadgeDefs.Event', str]  #: Badge type.
    issuance_uri: string_formats.AtUri  #: AT URI of the place.stream.badge.issuance record.
    issuer: string_formats.Did  #: DID of the badge issuer.
    description: t.Optional[str] = None  #: Description from the badge definition.
    image_url: t.Optional[string_formats.Uri] = None  #: Resolved image URL for the badge icon.
    issuance_cid: t.Optional[str] = None  #: CID of the place.stream.badge.issuance record.
    name: t.Optional[str] = None  #: Display name from the badge definition.
    selected: t.Optional[bool] = None  #: Whether this badge is currently in the user's chat profile selection.

    py_type: t.Literal['place.stream.badge.defs#badgeIssuanceView'] = Field(
        default='place.stream.badge.defs#badgeIssuanceView', alias='$type', frozen=True
    )
