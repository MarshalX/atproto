from atproto import Client, models


def main() -> None:
    client = Client()
    client.login('my-handle', 'my-password')

    print('Home (Following):\n')

    # Get "Home" page. Use pagination (cursor + limit) to fetch all posts
    timeline = client.get_timeline(algorithm='reverse-chronological')
    for feed_view in timeline.feed:
        action = 'New Post'
        if isinstance(feed_view.reason, models.AppBskyFeedDefs.ReasonRepost):
            action_by = feed_view.reason.by.handle
            action = f'Reposted by @{action_by}'

        post = feed_view.post.record
        author = feed_view.post.author

        if models.is_record_type(post, models.AppBskyFeedPost):
            print(f'[{action}] {author.display_name}: {post.text}')


if __name__ == '__main__':
    main()
