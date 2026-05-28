#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Record(base.RecordModelBase):
    """Record model for :obj:`site.standard.theme.basic`."""

    accent: te.Annotated[
        t.Union['models.SiteStandardThemeColor.Rgb'], Field(discriminator='py_type')
    ]  #: Color used for links and button backgrounds.
    accent_foreground: te.Annotated[
        t.Union['models.SiteStandardThemeColor.Rgb'], Field(discriminator='py_type')
    ]  #: Color used for button text.
    background: te.Annotated[
        t.Union['models.SiteStandardThemeColor.Rgb'], Field(discriminator='py_type')
    ]  #: Color used for content background.
    foreground: te.Annotated[
        t.Union['models.SiteStandardThemeColor.Rgb'], Field(discriminator='py_type')
    ]  #: Color used for content text.

    py_type: t.Literal['site.standard.theme.basic'] = Field(
        default='site.standard.theme.basic', alias='$type', frozen=True
    )


class GetRecordResponse(base.SugarResponseModelBase):
    """Get record response for :obj:`models.SiteStandardThemeBasic.Record`."""

    uri: str  #: The URI of the record.
    value: 'models.SiteStandardThemeBasic.Record'  #: The record.
    cid: t.Optional[str] = None  #: The CID of the record.


class ListRecordsResponse(base.SugarResponseModelBase):
    """List records response for :obj:`models.SiteStandardThemeBasic.Record`."""

    records: t.Dict[str, 'models.SiteStandardThemeBasic.Record']  #: Map of URIs to records.
    cursor: t.Optional[str] = None  #: Next page cursor.


class CreateRecordResponse(base.SugarResponseModelBase):
    """Create record response for :obj:`models.SiteStandardThemeBasic.Record`."""

    uri: str  #: The URI of the record.
    cid: str  #: The CID of the record.
