import os

from atproto import Client, models
from atproto.exceptions import BadRequestError


def main() -> None:
    client = Client()
    me = client.login(os.environ['USERNAME'], os.environ['PASSWORD'])
    assert me is not None  # None only when the PDS does not serve Bluesky profiles

    try:
        current_profile_record = client.app.bsky.actor.profile.get(me.did, 'self')
        current_profile = current_profile_record.value
        swap_record_cid = current_profile_record.cid
    except BadRequestError:
        current_profile = models.AppBskyActorProfile.Record()
        swap_record_cid = None

    # set new values to update
    new_description = None
    new_display_name = None

    client.com.atproto.repo.put_record(
        models.ComAtprotoRepoPutRecord.Data(
            collection=models.ids.AppBskyActorProfile,
            repo=me.did,
            rkey='self',
            swap_record=swap_record_cid,
            record=models.AppBskyActorProfile.Record(
                avatar=current_profile.avatar,  # keep old avatar. to set a new one, you should upload blob first
                banner=current_profile.banner,  # keep old banner. to set a new one, you should upload blob first
                description=new_description or current_profile.description,
                display_name=new_display_name or current_profile.display_name,
            ),
        )
    )


if __name__ == '__main__':
    main()
