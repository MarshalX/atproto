CAR reader
==========

The CAR format (Content Addressable aRchives) can be used to store content addressable objects in the form of IPLD block data as a sequence of bytes; typically in a file with a .car filename extension.

The CAR format is intended as a serialized representation of any IPLD DAG (graph) as the concatenation of its blocks, plus a header that describes the graphs in the file (via root CIDs). The requirement for the blocks in a CAR to form coherent DAGs is not strict, so the CAR format may also be used to store arbitrary IPLD blocks.

Specification for v1: https://ipld.io/specs/transport/car/carv1/

.. automodule:: atproto_core.car
   :members:
   :undoc-members:
   :show-inheritance:
