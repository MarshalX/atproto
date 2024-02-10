import re
import typing as t
import urllib.request

from atproto import Client, models


def get_og_tags(url: str) -> t.Tuple[str, str, str]:
    if not url.startswith(('http:', 'https:')):
        raise ValueError("URL must start with 'http:' or 'https:'")
    with urllib.request.urlopen(url) as res:
        html = res.read().decode('utf-8')
    meta_pattern = re.compile(r'<meta property="og:.*?>')
    content_pattern = re.compile(r'<meta[^>]+content="([^"]+)"')
    og_tags = meta_pattern.findall(html)
    if not og_tags:
        raise ValueError('og tags not found.')

    og_image = next(filter(lambda x: 'og:image' in x, og_tags))
    og_image = content_pattern.match(og_image).group(1)
    og_title = next(filter(lambda x: 'og:title' in x, og_tags))
    og_title = content_pattern.match(og_title).group(1)
    og_description = next(filter(lambda x: 'og:description' in x, og_tags))
    og_description = content_pattern.match(og_description).group(1)
    return og_image, og_title, og_description


def main() -> None:
    client = Client()
    client.login('my-handle', 'my-password')

    url = 'https://github.com/MarshalX/atproto'
    text = 'Example post with embed external resource (link card) with og:image'

    # Download image from og:image url
    img_url, title, description = get_og_tags(url)
    img_fp = urllib.request.urlopen(img_url)
    thumb_ref = client.upload_blob(img_fp.read())
    # AppBskyEmbedExternal is the same as "link card" in the app
    embed_external = models.AppBskyEmbedExternal.Main(
        external=models.AppBskyEmbedExternal.External(
            title=title, description=description, uri=url, thumb=thumb_ref.blob
        )
    )
    client.send_post(text=text, embed=embed_external)


if __name__ == '__main__':
    main()
