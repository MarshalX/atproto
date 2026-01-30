##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

from pydantic import Field

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class MessageMe(base.ModelBase):
    """Definition model for :obj:`com.germnetwork.declaration`."""

    message_me_url: string_formats.Uri  #: Message me url.
    show_button_to: t.Union[t.Literal['usersIFollow'], t.Literal['everyone'], str]  #: Show button to.

    py_type: t.Literal['com.germnetwork.declaration#messageMe'] = Field(
        default='com.germnetwork.declaration#messageMe', alias='$type', frozen=True
    )


class Record(base.RecordModelBase):
    """Record model for :obj:`com.germnetwork.declaration`."""

    current_key: t.Union[str, bytes]  #: Current key.
    version: str  #: Version.
    continuity_proofs: t.Optional[t.List[t.Union[str, bytes]]] = None  #: Continuity proofs.
    key_package: t.Optional[t.Union[str, bytes]] = None  #: Key package.
    message_me: t.Optional['models.ComGermnetworkDeclaration.MessageMe'] = None  #: Message me.

    py_type: t.Literal['com.germnetwork.declaration'] = Field(
        default='com.germnetwork.declaration', alias='$type', frozen=True
    )


class GetRecordResponse(base.SugarResponseModelBase):
    """Get record response for :obj:`models.ComGermnetworkDeclaration.Record`."""

    uri: str  #: The URI of the record.
    value: 'models.ComGermnetworkDeclaration.Record'  #: The record.
    cid: t.Optional[str] = None  #: The CID of the record.


class ListRecordsResponse(base.SugarResponseModelBase):
    """List records response for :obj:`models.ComGermnetworkDeclaration.Record`."""

    records: t.Dict[str, 'models.ComGermnetworkDeclaration.Record']  #: Map of URIs to records.
    cursor: t.Optional[str] = None  #: Next page cursor.


class CreateRecordResponse(base.SugarResponseModelBase):
    """Create record response for :obj:`models.ComGermnetworkDeclaration.Record`."""

    uri: str  #: The URI of the record.
    cid: str  #: The CID of the record.
