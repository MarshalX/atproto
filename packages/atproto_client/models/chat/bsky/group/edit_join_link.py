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
    """Input data model for :obj:`chat.bsky.group.editJoinLink`."""

    convo_id: str  #: Convo id.
    join_rule: t.Optional['models.ChatBskyGroupDefs.JoinRule'] = None  #: Join rule.
    require_approval: t.Optional[bool] = None  #: Require approval.


class DataDict(t.TypedDict):
    convo_id: str  #: Convo id.
    join_rule: te.NotRequired[t.Optional['models.ChatBskyGroupDefs.JoinRule']]  #: Join rule.
    require_approval: te.NotRequired[t.Optional[bool]]  #: Require approval.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`chat.bsky.group.editJoinLink`."""

    join_link: 'models.ChatBskyGroupDefs.JoinLinkView'  #: Join link.
