Core
====

The hand-written machinery every generated model is built on.

.. grid:: 1 2 2 3
   :gutter: 3

   .. grid-item-card:: :octicon:`package;1em;sd-mr-1` base
      :link: /models/base
      :link-type: doc

      Base classes every generated model inherits from.

   .. grid-item-card:: :octicon:`file-media;1em;sd-mr-1` blob_ref
      :link: /models/blob_ref
      :link-type: doc

      References to blobs stored on a PDS.

   .. grid-item-card:: :octicon:`package;1em;sd-mr-1` common
      :link: /models/common
      :link-type: doc

      Types shared across the generated models.

   .. grid-item-card:: :octicon:`code;1em;sd-mr-1` dot_dict
      :link: /models/dot_dict
      :link-type: doc

      Dict wrapper that also allows attribute access.

   .. grid-item-card:: :octicon:`globe;1em;sd-mr-1` languages
      :link: /models/languages
      :link-type: doc

      ISO language codes used by posts.

   .. grid-item-card:: :octicon:`sync;1em;sd-mr-1` models_loader
      :link: /models/models_loader
      :link-type: doc

      Lazy import of the generated model modules.

   .. grid-item-card:: :octicon:`database;1em;sd-mr-1` record_registry
      :link: /models/record_registry
      :link-type: doc

      Registry mapping record NSIDs to their model.

   .. grid-item-card:: :octicon:`checklist;1em;sd-mr-1` string_formats
      :link: /models/string_formats
      :link-type: doc

      Validation of the AT Protocol string formats.

   .. grid-item-card:: :octicon:`arrow-switch;1em;sd-mr-1` type_conversion
      :link: /models/type_conversion
      :link-type: doc

      Conversion between models, dicts, and raw JSON.

   .. grid-item-card:: :octicon:`question;1em;sd-mr-1` unknown_type
      :link: /models/unknown_type
      :link-type: doc

      Fallback for records of an unrecognised type.

   .. grid-item-card:: :octicon:`question;1em;sd-mr-1` unknown_union
      :link: /models/unknown_union
      :link-type: doc

      Fallback for union members of an unrecognised type.

   .. grid-item-card:: :octicon:`tools;1em;sd-mr-1` utils
      :link: /models/utils
      :link-type: doc

      Helpers for working with model instances.

.. toctree::
   :hidden:
   :maxdepth: 3

   base </models/base>
   blob_ref </models/blob_ref>
   common </models/common>
   dot_dict </models/dot_dict>
   languages </models/languages>
   models_loader </models/models_loader>
   record_registry </models/record_registry>
   string_formats </models/string_formats>
   type_conversion </models/type_conversion>
   unknown_type </models/unknown_type>
   unknown_union </models/unknown_union>
   utils </models/utils>
