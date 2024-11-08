from typing import Optional

from atproto import Client, IdResolver, models

def fetch_posts(client: Client, resolver: IdResolver, url: str) -> Optional[models.app.bsky.feed.get_posts.Response]:
    """
    Fetches a post using its Bluesky URL.
    Args:
        client (Client): Authenticated Atproto client.
        resolver (IdResolver): Resolver instance for DID lookup.
        url (str): URL of the Bluesky post.
    Returns:
        Optional[models.Record]: The hydrated post record if found, otherwise None.
    """
    try:
        # Extract the handle and post ID from the URL
        parts = url.split('/')
        handle = parts[4]  # Username in the URL
        post_id = parts[6]  # Post ID in the URL
        # Resolve the DID for the username
        did = resolver.handle.resolve(handle)
        if not did:
            print(f'Could not resolve DID for handle "{handle}".')
            return None
        # Construct the `at://` URI for the post and fetch the post record
        at_uri = f'at://{did}/app.bsky.feed.post/{post_id}'
        return client.get_posts([at_uri])
    except (ValueError, KeyError) as e:
        print(f'Error fetching post for URL {url}: {e}')
        return None

def main() -> None:
    # Initialize client and authenticate
    client = Client()
    client.login('my-handle', 'my-password')

    # Initialize IdResolver for DID resolution
    resolver = IdResolver()

    # Define the URL of the post to fetch
    url = 'https://bsky.app/profile/danabra.mov/post/3lagnt6bpkc2l'

    # Fetch the post
    post_record = fetch_posts(client, resolver, url)

    # Display the post details
    if post_record:
        print(f'Post Content: {post_record.text}')
    else:
        print('Post could not be fetched.')

if __name__ == '__main__':
    main()
