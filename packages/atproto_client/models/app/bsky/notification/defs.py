##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

from pydantic import Field

from atproto_client.models import base


class RecordDeleted(base.ModelBase):
    """Definition model for :obj:`app.bsky.notification.defs`."""

    py_type: t.Literal['app.bsky.notification.defs#recordDeleted'] = Field(
        default='app.bsky.notification.defs#recordDeleted', alias='$type', frozen=True
    )
