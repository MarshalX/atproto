import random
import string
from pathlib import Path
from time import sleep, time

from atproto import Client, models
from atproto.exceptions import RequestErrorBase
from atproto_client.models.dot_dict import DotDict
from atproto_client.models.utils import get_or_create

# Comment from the author (@MarshalX):
# I did not expect that using the video service would be so complicated.
# It is out of atproto scope sometimes. For example, GET params are not described in the lexicon at all...
# The "Video processed successfully" responses with 4xx status codes are a bit strange too.
# Random filename generation on the client side, etc.


_FINISHED_STATES = ['JOB_STATE_COMPLETED', 'JOB_STATE_FAILED']


def _generate_random_filename(file_path: str) -> str:
    # Get the file extension
    file_extension = Path(file_path).suffix

    # Generate a random filename
    random_name = ''.join(random.choices(string.ascii_letters + string.digits, k=10))  # noqa: S311

    # Combine the random name with the same extension
    return f'{random_name}{file_extension}'


def main() -> None:
    client = Client()  # create a default client to get service tokens
    client.login('my-handle', 'my-password')

    # replace it with your own data
    post_text = 'Post with video from Python'
    video_path = 'video.mp4'
    video_alt = 'Text version of the video (ALT)'
    video_upload_timeout_sec = 60

    with open(video_path, 'rb') as f:
        video_data = f.read()

    video_client = Client('https://video.bsky.app')  # create a client for video service

    print('Getting upload limits...')
    upload_limits_service_token = client.com.atproto.server.get_service_auth(
        models.ComAtprotoServerGetServiceAuth.Params(
            aud='did:web:video.bsky.app',
            lxm='app.bsky.video.getUploadLimits',
        )
    ).token
    video_client._set_auth_headers(upload_limits_service_token)  # set token to get upload limits

    upload_limits = video_client.app.bsky.video.get_upload_limits()
    print('Video upload limits:', upload_limits)

    print('Uploading video...')
    upload_video_service_token = client.com.atproto.server.get_service_auth(
        models.ComAtprotoServerGetServiceAuth.Params(
            aud=client._access_jwt_payload.aud,
            lxm='com.atproto.repo.uploadBlob',
        )
    ).token
    video_client._set_auth_headers(upload_video_service_token)  # set token to upload videos

    try:
        video_upload_params = DotDict({'did': client.me.did, 'name': _generate_random_filename(video_path)})
        job_status = video_client.app.bsky.video.upload_video(
            video_data, params=video_upload_params, timeout=video_upload_timeout_sec
        ).job_status
        print('Video processing job has been started:', job_status)

        # wait until the video processing job is finished
        while job_status.state not in _FINISHED_STATES:
            job_status = video_client.app.bsky.video.get_job_status(
                models.AppBskyVideoGetJobStatus.Params(job_id=job_status.job_id)
            ).job_status
            print(f'[{time()}] Job state: {job_status.state}; progress: {job_status.progress}%')
            sleep(1)
    except RequestErrorBase as err:
        if err.response is None or not isinstance(err.response.content, DotDict):
            # if the response is not a job status, then raise the error
            raise err

        # for example, it returns 409 status code if the video already processed (cached)
        job_status = get_or_create(err.response.content.to_dict(), models.AppBskyVideoDefs.JobStatus)
        print('Video processing caught:', job_status)

        # but somehow it does not return enriched job status... so we need to refetch proper job status again...
        if job_status.state in _FINISHED_STATES:
            job_status = video_client.app.bsky.video.get_job_status(
                models.AppBskyVideoGetJobStatus.Params(job_id=job_status.job_id)
            ).job_status

    print('Full job status:', job_status)

    blob = job_status.blob
    if not blob:
        print('Video processing failed (blob was not created):', job_status.error)
        return

    print(job_status.message)

    embed_video = models.AppBskyEmbedVideo.Main(video=blob, alt=video_alt)
    created_post = client.send_post(post_text, embed=embed_video)
    print('Post with video has been created:', created_post.uri)


if __name__ == '__main__':
    main()
