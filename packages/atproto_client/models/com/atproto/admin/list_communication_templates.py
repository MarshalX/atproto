##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

from pydantic import Field

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Response(base.ResponseModelBase):
    """Output data model for :obj:`com.atproto.admin.listCommunicationTemplates`."""

    communication_templates: t.List['models.ComAtprotoAdminDefs.CommunicationTemplateView'] = Field(
        alias='communicationTemplates'
    )  #: Communication templates.
