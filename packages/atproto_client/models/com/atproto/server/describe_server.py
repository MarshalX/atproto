##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Response(base.ResponseModelBase):
    """Output data model for :obj:`com.atproto.server.describeServer`."""

    available_user_domains: t.List[str]  #: List of domain suffixes that can be used in account handles.
    invite_code_required: t.Optional[
        bool
    ] = None  #: If true, an invite code must be supplied to create an account on this instance.
    links: t.Optional['models.ComAtprotoServerDescribeServer.Links'] = None  #: URLs of service policy documents.
    phone_verification_required: t.Optional[
        bool
    ] = None  #: If true, a phone verification token must be supplied to create an account on this instance.


class Links(base.ModelBase):
    """Definition model for :obj:`com.atproto.server.describeServer`."""

    privacy_policy: t.Optional[str] = None  #: Privacy policy.
    terms_of_service: t.Optional[str] = None  #: Terms of service.

    py_type: te.Literal['com.atproto.server.describeServer#links'] = Field(
        default='com.atproto.server.describeServer#links', alias='$type', frozen=True
    )
