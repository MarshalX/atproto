##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Data(base.DataModelBase):
    """Input data model for :obj:`chat.bsky.group.createJoinLink`."""

    convo_id: str  #: Convo id.
    join_rule: 'models.ChatBskyGroupDefs.JoinRule'  #: Join rule.
    require_approval: t.Optional[bool] = False  #: Require approval.


class DataDict(t.TypedDict):
    convo_id: str  #: Convo id.
    join_rule: 'models.ChatBskyGroupDefs.JoinRule'  #: Join rule.
    require_approval: te.NotRequired[t.Optional[bool]]  #: Require approval.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`chat.bsky.group.createJoinLink`."""

    join_link: 'models.ChatBskyGroupDefs.JoinLinkView'  #: Join link.
