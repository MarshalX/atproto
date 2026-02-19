##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class MessageMe(base.ModelBase):
    """Definition model for :obj:`com.germnetwork.declaration`."""

    message_me_url: string_formats.Uri = Field(
        min_length=1, max_length=2047
    )  #: A URL to present to an account that does not have its own com.germnetwork.declaration record, must have an empty fragment component, where the app should fill in the fragment component with the DIDs of the two accounts who wish to message each other.
    show_button_to: t.Union[t.Literal['none'], t.Literal['usersIFollow'], t.Literal['everyone'], str] = Field(
        min_length=1, max_length=100
    )  #: The policy of who can message the account, this value is included in the keyPackage, but is duplicated here to allow applications to decide if they should show a 'Message on Germ' button to the viewer.

    py_type: t.Literal['com.germnetwork.declaration#messageMe'] = Field(
        default='com.germnetwork.declaration#messageMe', alias='$type', frozen=True
    )


class Record(base.RecordModelBase):
    """Record model for :obj:`com.germnetwork.declaration`."""

    current_key: t.Union[str, bytes]  #: Opaque value, an ed25519 public key prefixed with a byte enum.
    version: str = Field(
        min_length=5, max_length=14
    )  #: Semver version number, without pre-release or build information, for the format of opaque content.
    continuity_proofs: te.Annotated[t.Optional[t.List[t.Union[str, bytes]]], Field(max_length=1000)] = (
        None  #: Array of opaque values to allow for key rolling.
    )
    key_package: t.Optional[t.Union[str, bytes]] = (
        None  #: Opaque value, contains MLS KeyPackage(s), and other signature data, and is signed by the currentKey.
    )
    message_me: t.Optional['models.ComGermnetworkDeclaration.MessageMe'] = (
        None  #: Controls who can message this account.
    )

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
