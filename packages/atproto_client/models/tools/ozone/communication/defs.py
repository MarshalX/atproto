##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

from atproto_client.models import base


class TemplateView(base.ModelBase):
    """Definition model for :obj:`tools.ozone.communication.defs`."""

    content_markdown: str  #: Subject of the message, used in emails.
    created_at: str  #: Created at.
    disabled: bool  #: Disabled.
    id: str  #: Id.
    last_updated_by: str  #: DID of the user who last updated the template.
    name: str  #: Name of the template.
    updated_at: str  #: Updated at.
    subject: t.Optional[str] = None  #: Content of the template, can contain markdown and variable placeholders.

    py_type: te.Literal['tools.ozone.communication.defs#templateView'] = Field(
        default='tools.ozone.communication.defs#templateView', alias='$type', frozen=True
    )
