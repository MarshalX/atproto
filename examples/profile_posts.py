from atproto import Client


def main(client: Client, handle: str) -> None:
    print(f'\nProfile Posts of {handle}:\n\n')

    # Get profile's posts. Use pagination (cursor + limit) to fetch all
    profile_feed = client.get_author_feed(actor=handle)
    for feed_view in profile_feed.feed:
        print('-', feed_view.post.record.text)


if __name__ == '__main__':
    at_client = Client()
    at_client.login('my-handle', 'my-password')

    while True:
        input_handle = input('\nPlease, enter the handle of the user: ')
        main(at_client, input_handle)
