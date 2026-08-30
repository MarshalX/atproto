com.atproto.identity
====================

Handles, DIDs, and identity resolution.

.. automodule:: atproto_client.models.com.atproto.identity
   :members:
   :show-inheritance:
   :undoc-members:

.. grid:: 1 2 2 3
   :gutter: 3

   .. grid-item-card:: :octicon:`code;1em;sd-mr-1` defs
      :link: /models/com/atproto/identity/defs
      :link-type: doc

      Shared type definitions.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getRecommendedDidCredentials
      :link: /models/com/atproto/identity/getRecommendedDidCredentials
      :link-type: doc

      Describe the credentials that should be included in the DID doc of an account that is migrating to this service.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` refreshIdentity
      :link: /models/com/atproto/identity/refreshIdentity
      :link-type: doc

      Request that the server re-resolve an identity (DID and handle).

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` requestPlcOperationSignature
      :link: /models/com/atproto/identity/requestPlcOperationSignature
      :link-type: doc

      Request an email with a code to in order to request a signed PLC operation.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` resolveDid
      :link: /models/com/atproto/identity/resolveDid
      :link-type: doc

      Resolves DID to DID document.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` resolveHandle
      :link: /models/com/atproto/identity/resolveHandle
      :link-type: doc

      Resolves an atproto handle (hostname) to a DID.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` resolveIdentity
      :link: /models/com/atproto/identity/resolveIdentity
      :link-type: doc

      Resolves an identity (DID or Handle) to a full identity (DID document and verified handle).

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` signPlcOperation
      :link: /models/com/atproto/identity/signPlcOperation
      :link-type: doc

      Signs a PLC operation to update some value(s) in the requesting DID's document.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` submitPlcOperation
      :link: /models/com/atproto/identity/submitPlcOperation
      :link-type: doc

      Validates a PLC operation to ensure that it doesn't violate a service's constraints or get the identity into a bad state, then submits it to the PLC registry

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` updateHandle
      :link: /models/com/atproto/identity/updateHandle
      :link-type: doc

      Updates the current account's handle.

.. toctree::
   :hidden:
   :maxdepth: 1

   defs </models/com/atproto/identity/defs>
   getRecommendedDidCredentials </models/com/atproto/identity/getRecommendedDidCredentials>
   refreshIdentity </models/com/atproto/identity/refreshIdentity>
   requestPlcOperationSignature </models/com/atproto/identity/requestPlcOperationSignature>
   resolveDid </models/com/atproto/identity/resolveDid>
   resolveHandle </models/com/atproto/identity/resolveHandle>
   resolveIdentity </models/com/atproto/identity/resolveIdentity>
   signPlcOperation </models/com/atproto/identity/signPlcOperation>
   submitPlcOperation </models/com/atproto/identity/submitPlcOperation>
   updateHandle </models/com/atproto/identity/updateHandle>
