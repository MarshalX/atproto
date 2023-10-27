##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


from pydantic import Field

from atproto.xrpc_client.models import base


class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.server.reserveSigningKey`."""

    signing_key: str = Field(alias='signingKey')  #: Public signing key in the form of a did:key.