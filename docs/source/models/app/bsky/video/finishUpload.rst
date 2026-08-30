app.bsky.video.finishUpload
===========================

Finish an upload. This call is idempotent and safe to retry. On deduplication completedJobId may differ from the input jobId; poll getJobStatus with completedJobId. Probe-based validation failures surface later as JOB_STATE_FAILED from getJobStatus, not as errors from this call.

.. automodule:: atproto_client.models.app.bsky.video.finish_upload
   :members:
   :show-inheritance:
   :undoc-members:
