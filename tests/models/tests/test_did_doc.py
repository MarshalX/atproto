from atproto.xrpc_client import models
from atproto.xrpc_client.models import base, get_or_create
from tests.models.tests.utils import load_data_from_file

TEST_DATA = load_data_from_file('did_doc')


def test_did_doc_deserialization():
    model = get_or_create(TEST_DATA, models.ComAtprotoRepoDescribeRepo.Response)

    assert isinstance(model, models.ComAtprotoRepoDescribeRepo.Response)

    context = ['https://www.w3.org/ns/did/v1', 'https://w3id.org/security/suites/secp256k1-2019/v1']
    service = [{'id': '#atproto_pds', 'type': 'AtprotoPersonalDataServer', 'serviceEndpoint': 'https://bsky.social'}]

    assert isinstance(model.didDoc, base.DotDict)
    assert model.didDoc['@context'] == context
    assert model.didDoc['service'] == service
    assert model.didDoc.service == service
