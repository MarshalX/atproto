from atproto import Client, models


def main():
    client = Client()
    client.login('my-handle', 'my-password')

    from datetime import datetime

    text = 'example link'
    url = 'https://google.com'

    facets = [
        models.AppBskyRichtextFacet.Main(
            features=[models.AppBskyRichtextFacet.Link(uri=url)],
            # we should pass when our link starts and ends in the text
            # the example below selects all the text
            index=models.AppBskyRichtextFacet.ByteSlice(byteStart=0, byteEnd=len(text.encode('UTF-8'))),
        )
    ]

    client.com.atproto.repo.create_record(
        models.ComAtprotoRepoCreateRecord.Data(
            repo=client.me.did,  # or any another DID
            collection='app.bsky.feed.post',
            record=models.AppBskyFeedPost.Main(createdAt=datetime.now().isoformat(), text=text, facets=facets),
        )
    )


if __name__ == '__main__':
    main()
