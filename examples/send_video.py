from atproto import Client


def main() -> None:
    client = Client()
    client.login('my-handle', 'my-password')

    # replace the path to your video file
    with open('video.mp4', 'rb') as f:
        vid_data = f.read()

    client.send_video(text='Post with video from Python', video=vid_data, video_alt='Text version of the video (ALT)')


if __name__ == '__main__':
    main()
