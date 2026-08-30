app.bsky.video
==============

Video uploads and the status of their processing jobs.

.. automodule:: atproto_client.models.app.bsky.video
   :members:
   :show-inheritance:
   :undoc-members:

.. grid:: 1 2 2 3
   :gutter: 3

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` abortUpload
      :link: /models/app/bsky/video/abortUpload
      :link-type: doc

      Abort an upload only while it is created, releasing its quota reservation immediately.

   .. grid-item-card:: :octicon:`code;1em;sd-mr-1` defs
      :link: /models/app/bsky/video/defs
      :link-type: doc

      Shared type definitions.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` finishUpload
      :link: /models/app/bsky/video/finishUpload
      :link-type: doc

      Finish an upload.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getJobStatus
      :link: /models/app/bsky/video/getJobStatus
      :link-type: doc

      Get status details for a video processing job.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getUploadLimits
      :link: /models/app/bsky/video/getUploadLimits
      :link-type: doc

      Get video upload limits for the authenticated user.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getUploadStatus
      :link: /models/app/bsky/video/getUploadStatus
      :link-type: doc

      Get the authoritative status of the upload phase.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` startUpload
      :link: /models/app/bsky/video/startUpload
      :link-type: doc

      Start a multipart video upload.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` uploadPart
      :link: /models/app/bsky/video/uploadPart
      :link-type: doc

      Upload one part.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` uploadVideo
      :link: /models/app/bsky/video/uploadVideo
      :link-type: doc

      Upload a video to be processed then stored on the PDS.

.. toctree::
   :hidden:
   :maxdepth: 1

   abortUpload </models/app/bsky/video/abortUpload>
   defs </models/app/bsky/video/defs>
   finishUpload </models/app/bsky/video/finishUpload>
   getJobStatus </models/app/bsky/video/getJobStatus>
   getUploadLimits </models/app/bsky/video/getUploadLimits>
   getUploadStatus </models/app/bsky/video/getUploadStatus>
   startUpload </models/app/bsky/video/startUpload>
   uploadPart </models/app/bsky/video/uploadPart>
   uploadVideo </models/app/bsky/video/uploadVideo>
