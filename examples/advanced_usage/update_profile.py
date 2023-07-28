import os

from atproto import Client, models


def main():
    client = Client()
    client.login(os.environ['USERNAME'], os.environ['PASSWORD'])

    current_profile_record = client.com.atproto.repo.get_record(
        models.ComAtprotoRepoGetRecord.Params(
            collection=models.ids.AppBskyActorProfile,
            repo=client.me.did,
            rkey='self',
        )
    )
    current_profile = current_profile_record.value

    # set new values to update
    new_description = None
    new_display_name = 'I love Python'

    client.com.atproto.repo.put_record(
        models.ComAtprotoRepoPutRecord.Data(
            collection=models.ids.AppBskyActorProfile,
            repo=client.me.did,
            rkey='self',
            swapRecord=current_profile_record.cid,
            record=models.AppBskyActorProfile.Main(
                avatar=current_profile.avatar,
                banner=current_profile.banner,
                description=new_description or current_profile.description,
                displayName=new_display_name or current_profile.display_name,
            ),
        )
    )


if __name__ == '__main__':
    main()
