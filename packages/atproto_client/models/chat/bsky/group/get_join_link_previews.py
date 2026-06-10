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


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`chat.bsky.group.getJoinLinkPreviews`."""

    codes: t.List[str] = Field(min_length=1, max_length=50)  #: Codes.


class ParamsDict(t.TypedDict):
    codes: t.List[str]  #: Codes.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`chat.bsky.group.getJoinLinkPreviews`."""

    join_link_previews: t.List[
        te.Annotated[
            t.Union[
                'models.ChatBskyGroupDefs.JoinLinkPreviewView',
                'models.ChatBskyGroupDefs.DisabledJoinLinkPreviewView',
                'models.ChatBskyGroupDefs.InvalidJoinLinkPreviewView',
            ],
            Field(discriminator='py_type'),
        ]
    ]  #: Join link previews.
