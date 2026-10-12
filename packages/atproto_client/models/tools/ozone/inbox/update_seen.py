#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

from atproto_client.models import base, string_formats


class Data(base.DataModelBase):
    """Input data model for :obj:`tools.ozone.inbox.updateSeen`."""

    sections: t.List[t.Union[t.Literal['reports', 'subjects', 'accountStatus'], str]] = Field(
        min_length=1
    )  #: Sections.
    seen_at: t.Optional[string_formats.DateTime] = (
        None  #: Mark each requested section read up to this instant. Defaults to server time and is clamped to server time when in the future. Newer existing watermarks are preserved independently for each section.
    )


class DataDict(t.TypedDict):
    sections: t.List[t.Union[t.Literal['reports', 'subjects', 'accountStatus'], str]]  #: Sections.
    seen_at: te.NotRequired[
        t.Optional[string_formats.DateTime]
    ]  #: Mark each requested section read up to this instant. Defaults to server time and is clamped to server time when in the future. Newer existing watermarks are preserved independently for each section.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.inbox.updateSeen`."""

    seen_at: string_formats.DateTime  #: The earliest resulting watermark across the requested sections, in UTC. Every requested section is read through this instant; individual sections may already have newer watermarks.
