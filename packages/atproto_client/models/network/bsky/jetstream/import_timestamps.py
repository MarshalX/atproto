#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

from atproto_client.models import base


class Data(base.DataModelBase):
    """Input data model for :obj:`network.bsky.jetstream.importTimestamps`."""

    path: str  #: Server-local path to the plain (uncompressed) import CSV, resolved within the configured import directory. May be relative to that directory or an absolute path inside it.


class DataDict(t.TypedDict):
    path: str  #: Server-local path to the plain (uncompressed) import CSV, resolved within the configured import directory. May be relative to that directory or an absolute path inside it.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`network.bsky.jetstream.importTimestamps`."""

    job: str  #: Opaque job id. Poll getImportStatus with this id to observe progress and the terminal result.
