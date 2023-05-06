##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


from dataclasses import dataclass
from typing import List, Optional

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

    availableUserDomains: List[str]
    inviteCodeRequired: Optional[bool] = None
    links: Optional['models.ComAtprotoServerDescribeServer.Links'] = None


@dataclass
class Links(base.ModelBase):

    """Definition model for :obj:`com.atproto.server.describeServer`.

    Attributes:
        privacyPolicy: Privacy policy.
        termsOfService: Terms of service.
    """

    privacyPolicy: Optional[str] = None
    termsOfService: Optional[str] = None
