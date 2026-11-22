#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Data(base.DataModelBase):
    """Input data model for :obj:`com.atproto.space.authorizeSpaceSync`."""

    credential_key: str  #: P-256 did:key that the credential is bound to.
    space: string_formats.SpaceRef  #: Space.
    client_attestation: t.Optional[str] = None  #: Client attestation.
    delegation_token: t.Optional[str] = None  #: Obtained from getDelegationToken.
    notify: t.Optional['models.ComAtprotoSpaceAuthorizeSpaceSync.Notify'] = (
        None  #: Register an endpoint to be notified of updates to the space via notifySpaceUpdate. The registration stays active while this credential is valid. After it expires, the endpoint receives only a prompt to reauthorize, or notice of the space's deletion.
    )


class DataDict(t.TypedDict):
    credential_key: str  #: P-256 did:key that the credential is bound to.
    space: string_formats.SpaceRef  #: Space.
    client_attestation: te.NotRequired[t.Optional[str]]  #: Client attestation.
    delegation_token: te.NotRequired[t.Optional[str]]  #: Obtained from getDelegationToken.
    notify: te.NotRequired[
        t.Optional['models.ComAtprotoSpaceAuthorizeSpaceSync.Notify']
    ]  #: Register an endpoint to be notified of updates to the space via notifySpaceUpdate. The registration stays active while this credential is valid. After it expires, the endpoint receives only a prompt to reauthorize, or notice of the space's deletion.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`com.atproto.space.authorizeSpaceSync`."""

    credential: str  #: Credential.
    space_rev: t.Optional[string_formats.Tid] = (
        None  #: The space's current revision. Omitted before the space's first update.
    )


class Notify(base.ModelBase):
    """Definition model for :obj:`com.atproto.space.authorizeSpaceSync`."""

    endpoint: string_formats.Uri  #: Base HTTPS URL that notification methods are called against.
    token: str = Field(
        max_length=512
    )  #: Opaque secret, included in the body of each request to the endpoint. The endpoint and token together identify the registration, so the token should stay the same across authorizations.

    py_type: t.Literal['com.atproto.space.authorizeSpaceSync#notify'] = Field(
        default='com.atproto.space.authorizeSpaceSync#notify', alias='$type', frozen=True
    )
