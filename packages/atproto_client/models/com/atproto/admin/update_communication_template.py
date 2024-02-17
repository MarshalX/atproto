##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te

from atproto_client.models import base


class Data(base.DataModelBase):
    """Input data model for :obj:`com.atproto.admin.updateCommunicationTemplate`."""

    id: str  #: ID of the template to be updated.
    content_markdown: t.Optional[
        str
    ] = None  #: Content of the template, markdown supported, can contain variable placeholders.
    disabled: t.Optional[bool] = None  #: Disabled.
    name: t.Optional[str] = None  #: Name of the template.
    subject: t.Optional[str] = None  #: Subject of the message, used in emails.
    updated_by: t.Optional[str] = None  #: DID of the user who is updating the template.


class DataDict(te.TypedDict):
    id: str  #: ID of the template to be updated.
    content_markdown: te.NotRequired[
        t.Optional[str]
    ]  #: Content of the template, markdown supported, can contain variable placeholders.
    disabled: te.NotRequired[t.Optional[bool]]  #: Disabled.
    name: te.NotRequired[t.Optional[str]]  #: Name of the template.
    subject: te.NotRequired[t.Optional[str]]  #: Subject of the message, used in emails.
    updated_by: te.NotRequired[t.Optional[str]]  #: DID of the user who is updating the template.
