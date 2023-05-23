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

    """Output data model for :obj:`com.atproto.server.describeServer`."""

    availableUserDomains: t.List[str]  #: Available user domains.
    inviteCodeRequired: t.Optional[bool] = None  #: Invite code required.
    links: t.Optional['models.ComAtprotoServerDescribeServer.Links'] = None  #: Links.


@dataclass
class Links(base.ModelBase):

    """Definition model for :obj:`com.atproto.server.describeServer`."""

    privacyPolicy: t.Optional[str] = None  #: Privacy policy.
    termsOfService: t.Optional[str] = None  #: Terms of service.

    _type: str = 'com.atproto.server.describeServer#links'
