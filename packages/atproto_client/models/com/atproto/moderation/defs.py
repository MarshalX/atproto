##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

if t.TYPE_CHECKING:
    from atproto_client import models

ReasonType = t.Union[
    'models.ComAtprotoModerationDefs.ReasonSpam',
    'models.ComAtprotoModerationDefs.ReasonViolation',
    'models.ComAtprotoModerationDefs.ReasonMisleading',
    'models.ComAtprotoModerationDefs.ReasonSexual',
    'models.ComAtprotoModerationDefs.ReasonRude',
    'models.ComAtprotoModerationDefs.ReasonOther',
    'models.ComAtprotoModerationDefs.ReasonAppeal',
    str,
]  #: Reason type

ReasonSpam = t.Literal[
    'com.atproto.moderation.defs#reasonSpam'
]  #: Spam: frequent unwanted promotion, replies, mentions

ReasonViolation = t.Literal[
    'com.atproto.moderation.defs#reasonViolation'
]  #: Direct violation of server rules, laws, terms of service

ReasonMisleading = t.Literal[
    'com.atproto.moderation.defs#reasonMisleading'
]  #: Misleading identity, affiliation, or content

ReasonSexual = t.Literal['com.atproto.moderation.defs#reasonSexual']  #: Unwanted or mislabeled sexual content

ReasonRude = t.Literal[
    'com.atproto.moderation.defs#reasonRude'
]  #: Rude, harassing, explicit, or otherwise unwelcoming behavior

ReasonOther = t.Literal[
    'com.atproto.moderation.defs#reasonOther'
]  #: Other: reports not falling under another report category

ReasonAppeal = t.Literal[
    'com.atproto.moderation.defs#reasonAppeal'
]  #: Appeal: appeal a previously taken moderation action
