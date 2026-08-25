"""Build video delivery URLs, a poster frame, player markup, and a streaming manifest.

Video needs resource_type="video". CloudinaryVideo sets it for you; plain cloudinary_url()
does not, which is the usual cause of 404s when reusing image code.

Prerequisites: set CLOUDINARY_URL in your environment (Console > Settings > API Keys).
Run examples/upload-large-video.py first so there is a video to build URLs for.

Building a URL makes no API call, so this prints URLs whether or not the asset exists.

Related:
- Task doc: cloudinary/docs/transform-and-deliver-video.md
- For images: examples/transform-and-deliver-image.py
- Video transformation reference:
  https://cloudinary.com/documentation/video_manipulation_and_delivery.md
"""
import cloudinary

# Configuration is read from CLOUDINARY_URL automatically.

PUBLIC_ID = "examples/product-tour"


def main() -> None:
    video = cloudinary.CloudinaryVideo(PUBLIC_ID)

    print("Scaled video URL:")
    print("  " + video.build_url(width=1280, crop="scale", quality="auto", secure=True))

    print("A 6-second clip, best codec per browser:")
    print("  " + video.build_url(
        start_offset="2.0", end_offset="8.0", width=720, crop="scale",
        video_codec="auto", audio_codec="aac", quality="auto", secure=True,
    ))

    print("Poster frame at 3.5s (an image derived from the video):")
    print("  " + video.video_thumbnail(width=640, start_offset="3.5", secure=True))

    print("HLS manifest (needs the streaming profile's renditions to exist):")
    print("  " + video.build_url(streaming_profile="hd", format="m3u8", secure=True))

    print("Player markup:")
    print("  " + video.video(width=640, controls=True, source_types=["mp4", "webm"], secure=True))


if __name__ == "__main__":
    try:
        main()
    except ValueError as error:
        print(f"Configuration error: {error}")
        print("Set CLOUDINARY_URL (Console > Settings > API Keys).")
        raise SystemExit(1)
