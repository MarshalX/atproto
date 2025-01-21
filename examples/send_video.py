from atproto import Client, models


def main() -> None:
    client = Client()
    client.login('my-handle', 'my-password')

    # replace the path to your video file
    with open('video.mp4', 'rb') as f:
        vid_data = f.read()
        
    # Add video aspect ratio to prevent default 1:1 aspect ratio
    # Replace with your desired aspect ratio
    aspect_ratio = models.AppBskyEmbedDefs.AspectRatio(height=100, width=100)

    client.send_video(
        text='Post with video from Python',
        video=vid_data,
        video_alt='Text version of the video (ALT)',
        video_aspect_ratio=aspect_ratio,
    )


if __name__ == '__main__':
    main()
