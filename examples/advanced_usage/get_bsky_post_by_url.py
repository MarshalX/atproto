from typing import Optional

from atproto import Client, IdResolver, models


def fetch_posts(client: Client, resolver: IdResolver, url: str) -> Optional[models.AppBskyFeedPost.Record]:
    """Fetch a post using its Bluesky URL.

    Args:
        client (Client): Authenticated Atproto client.
        resolver (IdResolver): Resolver instance for DID lookup.
        url (str): URL of the Bluesky post.
    Returns:
        :obj:`models.AppBskyFeedPost.Record`: Post if found, otherwise None.
    """
    try:
        # Extract the handle and post rkey from the URL
        url_parts = url.split('/')
        handle = url_parts[4]  # Username in the URL
        post_rkey = url_parts[6]  # Post Record Key in the URL

        # Resolve the DID for the username
        did = resolver.handle.resolve(handle)
        if not did:
            print(f'Could not resolve DID for handle "{handle}".')
            return None

        # Fetch the post record
        return client.get_post(post_rkey, did).value
    except (ValueError, KeyError) as e:
        print(f'Error fetching post for URL {url}: {e}')
        return None


def main() -> None:
    # Initialize a client and authenticate
    client = Client()
    client.login('my-handle', 'my-password')

    # Initialize IdResolver for DID resolution
    resolver = IdResolver()

    # Define the URL of the post to fetch
    bsky_post_url = 'https://bsky.app/profile/test.marshal.dev/post/3laqsdrwwgc24'

    # Fetch the post
    post_record = fetch_posts(client, resolver, bsky_post_url)

    # Display the post details
    if post_record:
        print(f'Post content: {post_record.text}')
    else:
        print('Post could not be fetched.')


if __name__ == '__main__':
    main()
