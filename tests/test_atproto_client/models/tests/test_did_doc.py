from atproto_client import models
from atproto_client.models import get_or_create
from atproto_client.models.dot_dict import DotDict

from tests.test_atproto_client.models.tests.utils import load_data_from_file


def load_test_data() -> dict:
    return load_data_from_file('did_doc')


def test_did_doc_deserialization() -> None:
    model = get_or_create(load_test_data(), models.ComAtprotoRepoDescribeRepo.Response)

    assert isinstance(model, models.ComAtprotoRepoDescribeRepo.Response)

    context = [
        'https://www.w3.org/ns/did/v1',
        'https://w3id.org/security/multikey/v1',
        'https://w3id.org/security/suites/secp256k1-2019/v1',
    ]
    service = [
        {
            'id': '#atproto_pds',
            'type': 'AtprotoPersonalDataServer',
            'serviceEndpoint': 'https://shimeji.us-east.host.bsky.network',
        }
    ]
    verification_method_id = 'did:plc:kvwvcn5iqfooopmyzvb4qzba#atproto'

    assert isinstance(model.did_doc, DotDict)
    assert model.did_doc['@context'] == context
    assert model.did_doc['service'] == service
    assert model.did_doc.service == service
    assert model.did_doc.verificationMethod[0].id == verification_method_id
