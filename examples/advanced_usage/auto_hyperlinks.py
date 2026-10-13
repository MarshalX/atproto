from atproto import Client


def main() -> None:
    client = Client()
    client.login('my-handle', 'my-password')

    text = 'Hello @bsky.app! #greetings from https://github.com/MarshalX/atproto and atproto.blue - $DPZ time! 🍕'

    # Detects @mentions, links, #hashtags and $cashtags
    # Mentions are resolved to DIDs; unresolved ones are dropped
    facets = client.detect_facets(text)

    client.send_post(text, facets=facets)


if __name__ == '__main__':
    main()
