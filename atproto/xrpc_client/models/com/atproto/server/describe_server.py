##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.server.describeServer`."""

    available_user_domains: t.List[str] = Field(alias='availableUserDomains')  #: Available user domains.
    invite_code_required: t.Optional[bool] = Field(default=None, alias='inviteCodeRequired')  #: Invite code required.
    links: t.Optional['models.ComAtprotoServerDescribeServer.Links'] = None  #: Links.


class Links(base.ModelBase):

    """Definition model for :obj:`com.atproto.server.describeServer`."""

    privacy_policy: t.Optional[str] = Field(default=None, alias='privacyPolicy')  #: Privacy policy.
    terms_of_service: t.Optional[str] = Field(default=None, alias='termsOfService')  #: Terms of service.

    py_type: te.Literal['com.atproto.server.describeServer#links'] = Field(
        default='com.atproto.server.describeServer#links', alias='$type', frozen=True
    )
