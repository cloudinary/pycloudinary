"""Upload a large video in chunks with upload_large, then print its delivery URLs.

Downloads a sample video from the Cloudinary demo account, then uploads it in chunks.

upload_large defaults to resource_type="raw" - a raw upload succeeds but no video
transformation will ever work on it, so resource_type="video" is passed explicitly below.

Prerequisites: set CLOUDINARY_URL in your environment (Console > Settings > API Keys).

Related:
- Task doc: cloudinary/docs/upload-large-video.md
- Delivery, players, and streaming: examples/transform-and-deliver-video.py
"""
import os
import tempfile
from urllib.request import urlretrieve

import cloudinary
import cloudinary.exceptions
import cloudinary.uploader

# Configuration is read from CLOUDINARY_URL automatically.

SAMPLE_VIDEO = "https://res.cloudinary.com/demo/video/upload/dog.mp4"


def sample_video_path() -> str:
    path = os.path.join(tempfile.gettempdir(), "cloudinary-example-dog.mp4")
    if not os.path.exists(path):
        print(f"Downloading a sample video to {path} ...")
        urlretrieve(SAMPLE_VIDEO, path)
    return path


def main() -> None:
    path = sample_video_path()
    print(f"Uploading {path} ({os.path.getsize(path) / 1e6:.1f} MB) ...")

    result = cloudinary.uploader.upload_large(
        path,
        resource_type="video",          # required: the default is "raw"
        public_id="examples/product-tour",
        chunk_size=6000000,             # 6 MB; the default is 20 MB, the minimum 5 MB
    )

    print(f"Stored reference: {result['asset_id']}")
    print(f"Public ID:        {result['public_id']}")
    print(f"Duration:         {result['duration']}s")
    print(f"Format:           {result['format']}")
    print(f"Original URL:     {result['secure_url']}")

    video = cloudinary.CloudinaryVideo(result["public_id"])
    scaled = video.build_url(width=720, crop="scale", quality="auto", secure=True)
    print(f"Scaled URL:       {scaled}")
    print(f"Poster frame:     {video.video_thumbnail(width=720, secure=True)}")


if __name__ == "__main__":
    try:
        main()
    except cloudinary.exceptions.Error as error:
        print(f"Upload failed: {error}")
        raise SystemExit(1)
    except ValueError as error:
        print(f"Configuration error: {error}")
        print("Set CLOUDINARY_URL (Console > Settings > API Keys).")
        raise SystemExit(1)
