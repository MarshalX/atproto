import re
import typing as t

from atproto import Client, models

def extract_url_byte_positions(
    text: str, *, encoding: str = 'UTF-8'
) -> t.List[t.Tuple[str, int, int]]:
    """This function will detect any links beginning with http or https"""
    encoded_text = text.encode(encoding)

    # Adjusted URL matching pattern
    pattern = rb'https?://[^ \n\r\t]*'

    matches = re.finditer(pattern, encoded_text)
    url_byte_positions = []

    for match in matches:
        url_bytes = match.group(0)
        url = url_bytes.decode(encoding)
        url_byte_positions.append((url, match.start(), match.end()))

    return url_byte_positions

def main() -> None:
    client = Client()
    client.login('my-handle', 'my-password')

    text = 'Example post with automatic link detection https://github.com/MarshalX/atproto, http://google.com and https://apple.com'

    # Determine locations of URLs in the post's text
    url_positions = extract_url_byte_positions(text)
    facets = []

    # AT requires URL to include http or https when creating the facet
    for link in url_positions:
        uri = link[0]
        facets.append(
            models.AppBskyRichtextFacet.Main(
                features=[models.AppBskyRichtextFacet.Link(uri=uri)],
                index=models.AppBskyRichtextFacet.ByteSlice(byte_start=link[1], byte_end=link[2]),
            )
        )

    client.com.atproto.repo.create_record(
        models.ComAtprotoRepoCreateRecord.Data(
            repo=client.me.did,
            collection=models.ids.AppBskyFeedPost,
            record=models.AppBskyFeedPost.Main(created_at=client.get_current_time_iso(), text=text, facets=facets),
        )
    )

if __name__ == '__main__':
    main()
