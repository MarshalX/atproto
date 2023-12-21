import typing as t

import typing_extensions as te
from atproto_core.cid import CID
from pydantic import BaseModel, ConfigDict, Field


class IpldLink(BaseModel):
    """CID representation in JSON."""

    link: str = Field(alias='$link')  #: CID.


class BlobRef(BaseModel):
    """Blob reference."""

    model_config = ConfigDict(extra='allow', populate_by_name=True, strict=True)

    mime_type: str = Field(alias='mimeType')  #: Mime type.
    size: int  #: Size in bytes.
    ref: t.Union[str, IpldLink]  #: CID.

    py_type: te.Literal['blob'] = Field(default='blob', alias='$type')

    @property
    def cid(self) -> 'CID':
        """Get CID."""
        if isinstance(self.ref, str):
            return CID.decode(self.ref)

        return CID.decode(self.ref.link)
