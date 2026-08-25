"""Build transformation and delivery URLs for an image already in Cloudinary.

URL generation is local - no network call and no credentials beyond the cloud name.
The derived asset is created by Cloudinary on first request and then served from CDN cache.

Prerequisites: set CLOUDINARY_URL in your environment. Run examples/upload-image.py first
to create the asset this script transforms, or pass any public ID as an argument.

Related:
- Task doc: cloudinary/docs/transform-and-deliver-image.md
- For video: examples/transform-and-deliver-video.py
- Every transformation parameter and its accepted values:
  https://cloudinary.com/documentation/transformation_reference.md
- Building transformations from a plain-language description: the
  cloudinary-transformations skill (npx skills add cloudinary-devs/skills)
"""
import cloudinary
import cloudinary.utils

# Configuration is read from CLOUDINARY_URL automatically.

PUBLIC_ID = "examples/uploaded-sample"


def main() -> None:
    image = cloudinary.CloudinaryImage(PUBLIC_ID)

    print("Optimized 400x400 fill:")
    print("  " + image.build_url(
        width=400, height=400, crop="fill", gravity="auto",
        fetch_format="auto", quality="auto", secure=True,
    ))

    print("Thumbnail focused on a face:")
    print("  " + image.build_url(
        width=150, height=150, crop="thumb", gravity="face",
        fetch_format="auto", quality="auto", secure=True,
    ))

    print("Chained - crop, then sharpen:")
    print("  " + image.build_url(
        transformation=[
            {"width": 600, "height": 600, "crop": "fill", "gravity": "auto"},
            {"effect": "sharpen"},
        ],
        fetch_format="auto", quality="auto", secure=True,
    ))

    # Generative effects are generic strings, not typed builders.
    print("Generative fill to a wide aspect ratio:")
    print("  " + image.build_url(
        background="gen_fill", width=1200, height=630, crop="pad", secure=True,
    ))

    # The functional form returns a (url, remaining_options) tuple - unpack it.
    url, _ = cloudinary.utils.cloudinary_url(
        PUBLIC_ID, width=300, crop="scale", fetch_format="auto", quality="auto", secure=True,
    )
    print("Via cloudinary_url():")
    print("  " + url)

    print("An <img> tag:")
    print("  " + image.image(
        width=300, crop="scale", fetch_format="auto", quality="auto",
        secure=True, alt="A sample image",
    ))


if __name__ == "__main__":
    try:
        main()
    except ValueError as error:
        print(f"Configuration error: {error}")
        print("Set CLOUDINARY_URL (Console > Settings > API Keys).")
        raise SystemExit(1)
