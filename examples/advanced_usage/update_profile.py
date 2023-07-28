import os

from atproto import Client, models


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
        swapRecord = current_profile_record.cid
    except:
        current_profile = models.AppBskyActorProfile.Main
        swapRecord = None

    # set new values to update
    new_description = None
    new_display_name = None
    new_avatar = None
    new_banner = None

    client.com.atproto.repo.put_record(
        models.ComAtprotoRepoPutRecord.Data(
            collection=models.ids.AppBskyActorProfile,
            repo=client.me.did,
            rkey='self',
            swapRecord=swapRecord,
            record=models.AppBskyActorProfile.Main(
                avatar=new_avatar or current_profile.avatar,
                banner=new_banner or current_profile.banner,
                description=new_description or current_profile.description,
                displayName=new_display_name or current_profile.displayName,
            ),
        )
    )


if __name__ == '__main__':
    main()
