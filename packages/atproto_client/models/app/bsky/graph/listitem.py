##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

from atproto_client.models import base


class Record(base.RecordModelBase):
    """Record model for :obj:`app.bsky.graph.listitem`."""

    created_at: str = Field(alias='createdAt')  #: Created at.
    list: str  #: List.
    subject: str  #: Subject.

    py_type: te.Literal['app.bsky.graph.listitem'] = Field(
        default='app.bsky.graph.listitem', alias='$type', frozen=True
    )


class Main(Record):
    def __init_subclass__(cls, **data: t.Any) -> None:
        import warnings

        warnings.warn('Main class is deprecated. Use Record class instead.', DeprecationWarning, stacklevel=2)
        super().__init_subclass__(**data)

    def __init__(self, **data: t.Any) -> None:
        import warnings

        warnings.warn('Main class is deprecated. Use Record class instead.', DeprecationWarning, stacklevel=2)
        super().__init__(**data)
