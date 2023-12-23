DID Document
============

Check out how to resolve a DID Document in :doc:`atproto_identity/identity`.

After a DID document has been resolved, atproto-specific information needs to be extracted. This parsing process is agnostic to the DID method used to resolve the document.

SDK automatically parses the DID document and provides a DID document object after resolving.

If you got a DID document from other sources, you can also parse it:

..  code-block:: python

    from atproto import Client, DidDocument

    client = Client()
    client.login('username', 'password')

    response = client.com.atproto.repo.describe_repo({'repo': 'did:plc:kvwvcn5iqfooopmyzvb4qzba'})
    did_doc = DidDocument.from_dict(response.did_doc)
    print(did_doc.get_pds_endpoint())
    print(did_doc.get_handle())


Read more about DID document in official documentation: https://atproto.com/specs/did

.. automodule:: atproto_core.did_doc
   :members:
   :undoc-members:
   :show-inheritance:
