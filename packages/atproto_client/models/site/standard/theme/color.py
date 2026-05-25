##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

from pydantic import Field

from atproto_client.models import base


class Rgb(base.ModelBase):
    """Definition model for :obj:`site.standard.theme.color`."""

    b: int = Field(ge=0, le=255)  #: B.
    g: int = Field(ge=0, le=255)  #: G.
    r: int = Field(ge=0, le=255)  #: R.

    py_type: t.Literal['site.standard.theme.color#rgb'] = Field(
        default='site.standard.theme.color#rgb', alias='$type', frozen=True
    )


class Rgba(base.ModelBase):
    """Definition model for :obj:`site.standard.theme.color`."""

    a: int = Field(ge=0, le=100)  #: A.
    b: int = Field(ge=0, le=255)  #: B.
    g: int = Field(ge=0, le=255)  #: G.
    r: int = Field(ge=0, le=255)  #: R.

    py_type: t.Literal['site.standard.theme.color#rgba'] = Field(
        default='site.standard.theme.color#rgba', alias='$type', frozen=True
    )
