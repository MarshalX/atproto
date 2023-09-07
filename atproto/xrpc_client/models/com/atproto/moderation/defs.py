##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te

if t.TYPE_CHECKING:
    from atproto.xrpc_client import models

ReasonType = t.Union[
    'models.ComAtprotoModerationDefs.ReasonSpam',
    'models.ComAtprotoModerationDefs.ReasonViolation',
    'models.ComAtprotoModerationDefs.ReasonMisleading',
    'models.ComAtprotoModerationDefs.ReasonSexual',
    'models.ComAtprotoModerationDefs.ReasonRude',
    'models.ComAtprotoModerationDefs.ReasonOther',
]  #: Reason type

ReasonSpam = te.Literal[
    'com.atproto.moderation.defs#reasonSpam'
]  #: Spam: frequent unwanted promotion, replies, mentions

ReasonViolation = te.Literal[
    'com.atproto.moderation.defs#reasonViolation'
]  #: Direct violation of server rules, laws, terms of service

ReasonMisleading = te.Literal[
    'com.atproto.moderation.defs#reasonMisleading'
]  #: Misleading identity, affiliation, or content

ReasonSexual = te.Literal['com.atproto.moderation.defs#reasonSexual']  #: Unwanted or mislabeled sexual content

ReasonRude = te.Literal[
    'com.atproto.moderation.defs#reasonRude'
]  #: Rude, harassing, explicit, or otherwise unwelcoming behavior

ReasonOther = te.Literal[
    'com.atproto.moderation.defs#reasonOther'
]  #: Other: reports not falling under another report category
