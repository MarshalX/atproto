import typing as t

import typing_extensions as te
from pydantic import BaseModel, ConfigDict, Field

if t.TYPE_CHECKING:
    from atproto.cid import CID


class BlobRefLink(BaseModel):
    link: str = Field(alias='$link')


class BlobRef(BaseModel):
    model_config = ConfigDict(extra='forbid')

    mime_type: str = Field(alias='mimeType')
    size: int
    ref: BlobRefLink

    py_type: te.Literal['blob'] = Field(default='blob', alias='$type')

    @property
    def cid(self) -> 'CID':
        from atproto.cid import CID

        return CID.decode(self.ref.link)
