##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t
from dataclasses import dataclass

from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


@dataclass
class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.server.describeServer`.

    Attributes:
        inviteCodeRequired: Invite code required.
        availableUserDomains: Available user domains.
        links: Links.
    """

    availableUserDomains: t.List[str]
    inviteCodeRequired: t.Optional[bool] = None
    links: t.Optional['models.ComAtprotoServerDescribeServer.Links'] = None


@dataclass
class Links(base.ModelBase):

    """Definition model for :obj:`com.atproto.server.describeServer`.

    Attributes:
        privacyPolicy: Privacy policy.
        termsOfService: Terms of service.
    """

    privacyPolicy: t.Optional[str] = None
    termsOfService: t.Optional[str] = None

    _type: str = 'com.atproto.server.describeServer#links'
