import typing as t

from pydantic import BaseModel, Field, ValidationError


class VerificationMethod(BaseModel):
    id: str
    type: str
    controller: str
    public_key_multibase: t.Optional[str] = Field(default=None, alias='publicKeyMultibase')


class Service(BaseModel):
    id: str
    type: str
    service_endpoint: t.Union[str, dict] = Field(alias='serviceEndpoint')


class DidDocument(BaseModel):
    id: str
    also_known_as: t.Optional[t.List[str]] = Field(default=None, alias='alsoKnownAs')
    verification_method: t.Optional[t.List['VerificationMethod']] = Field(default=None, alias='verificationMethod')
    service: t.Optional[t.List['Service']] = None


def is_valid_did_doc(did_doc: dict) -> bool:
    try:
        parse_did_doc(did_doc)
        return True
    except ValidationError:
        return False


def parse_did_doc(did_doc: dict) -> DidDocument:
    return DidDocument(**did_doc)
