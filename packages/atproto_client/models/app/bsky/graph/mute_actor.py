#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te

from atproto_client.models import base, string_formats


class Data(base.DataModelBase):
    """Input data model for :obj:`app.bsky.graph.muteActor`."""

    actor: string_formats.AtIdentifier  #: Actor.
    only_quoteposts: t.Optional[bool] = None  #: Restrict the mute to the account's quote posts. See onlyReposts.
    only_reposts: t.Optional[bool] = (
        None  #: Restrict the mute to the account's reposts. When any 'only' scope is set, just the scoped content is muted; when none are set, the account is fully muted. Repeat calls replace the stored scope rather than adding to it.
    )


class DataDict(t.TypedDict):
    actor: string_formats.AtIdentifier  #: Actor.
    only_quoteposts: te.NotRequired[
        t.Optional[bool]
    ]  #: Restrict the mute to the account's quote posts. See onlyReposts.
    only_reposts: te.NotRequired[
        t.Optional[bool]
    ]  #: Restrict the mute to the account's reposts. When any 'only' scope is set, just the scoped content is muted; when none are set, the account is fully muted. Repeat calls replace the stored scope rather than adding to it.
