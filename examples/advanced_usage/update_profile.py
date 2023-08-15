import os

from atproto import Client, models
from atproto.exceptions import BadRequestError


def main():
    client = Client()
    client.login(os.environ['USERNAME'], os.environ['PASSWORD'])

    try:
        current_profile_record = client.com.atproto.repo.get_record(
            models.ComAtprotoRepoGetRecord.Params(
                collection=models.ids.AppBskyActorProfile,
                repo=client.me.did,
                rkey='self',
            )
        )
        current_profile = current_profile_record.value
        swap_record_cid = current_profile_record.cid
    except BadRequestError:
        current_profile = swap_record_cid = None

    old_description = old_display_name = None
    if current_profile:
        old_description = current_profile.description
        old_display_name = current_profile.displayName

    # set new values to update
    new_description = None
    new_display_name = None

    client.com.atproto.repo.put_record(
        models.ComAtprotoRepoPutRecord.Data(
            collection=models.ids.AppBskyActorProfile,
            repo=client.me.did,
            rkey='self',
            swapRecord=swap_record_cid,
            record=models.AppBskyActorProfile.Main(
                avatar=current_profile.avatar,  # keep old avatar. to set a new one, you should upload blob first
                banner=current_profile.banner,  # keep old banner. to set a new one, you should upload blob first
                description=new_description or old_description,
                displayName=new_display_name or old_display_name,
            ),
        )
    )


if __name__ == '__main__':
    main()
