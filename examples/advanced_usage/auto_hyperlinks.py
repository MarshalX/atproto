from datetime import datetime
import re
from atproto import Client, models


def extract_url_byte_positions(text, aggressive=True, encoding='utf-8'):
    '''
    If aggressive is False, only links beginning http or https will be detected
    '''
    encoded_text = text.encode(encoding)

    if aggressive:
        pattern = rb'(?:[\w+]+\:\/\/)?(?:[\w\d-]+\.)*[\w-]+[\.\:]\w+\/?(?:[\/\?\=\&\#\.]?[\w-]+)+\/?'
    else:
        pattern = rb'https?\:\/\/(?:[\w\d-]+\.)*[\w-]+[\.\:]\w+\/?(?:[\/\?\=\&\#\.]?[\w-]+)+\/?'

    matches = re.finditer(pattern, encoded_text)
    url_byte_positions = []
    for match in matches:
        url_bytes = match.group(0)
        url = url_bytes.decode(encoding)
        url_byte_positions.append((url, match.start(), match.end()))
    
    return url_byte_positions


def main():
    client = Client()
    client.login('my-handle', 'my-password')

    text = 'Example post with automatic link detection https://github.com/MarshalX/atproto, google.com and apple.com'

    # Determine locations of URLs in the post text
    url_positions = extract_url_byte_positions(text, aggressive=True)
    facets = []

    #AT requires URL to include http or https when creating the facet. Appends to URL if not present
    for link in url_positions:
        uri = link[0] if "http" == link[0][0:4] else f"http://{link[0]}"
        facets.append(
                    models.AppBskyRichtextFacet.Main(
            features=[models.AppBskyRichtextFacet.Link(uri=uri)],
            index=models.AppBskyRichtextFacet.ByteSlice(byteStart=link[1], byteEnd=link[2]),
        )
        )

    client.com.atproto.repo.create_record(
        models.ComAtprotoRepoCreateRecord.Data(
            repo=client.me.did,
            collection=models.ids.AppBskyFeedPost,
            record=models.AppBskyFeedPost.Main(
                createdAt=datetime.now().isoformat(), text=text, facets=facets
            ),
        )
    )




if __name__ == '__main__':
    main()