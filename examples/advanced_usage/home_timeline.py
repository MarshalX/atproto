from atproto import Client


def main():
    client = Client()
    client.login('my-handle', 'my-password')

    print('Home (Following):\n\n')

    # Get "Home" page. Use pagination (cursor + limit) to fetch all posts
    timeline = client.bsky.feed.get_timeline({'algorithm': 'reverse-chronological'})
    for feed_view in timeline.feed:
        author = feed_view.post.author

        action = 'New Post'
        action_by = author.displayName
        if feed_view.reason:
            action = type(feed_view.reason).__name__.replace('Reason', '')
            action_by = feed_view.reason.by.displayName

        post = feed_view.post.record
        author = feed_view.post.author

        print(
            f'[{action} by {action_by}] Post author: {author.displayName}. Posted at {post.createdAt}. Post text: {post.text}'
        )


if __name__ == '__main__':
    main()
