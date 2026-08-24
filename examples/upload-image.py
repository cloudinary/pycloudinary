"""Upload an image and print its public ID and an optimized delivery URL.

Prerequisites: set CLOUDINARY_URL in your environment (Console > Settings > API Keys).
No account? Run examples/provision-claimable-cloud.py first.

Related:
- Task doc: cloudinary/docs/upload-image.md
- Delivery URLs: examples/transform-and-deliver-image.py
"""
import cloudinary
import cloudinary.exceptions
import cloudinary.uploader

# Configuration is read from CLOUDINARY_URL automatically.

SAMPLE_IMAGE = "https://res.cloudinary.com/demo/image/upload/sample.jpg"


def main() -> None:
    result = cloudinary.uploader.upload(
        SAMPLE_IMAGE,
        public_id="examples/uploaded-sample",
        tags=["example"],
        context={"alt": "A sample image uploaded by the pycloudinary example"},
    )

    # asset_id never changes; public_id changes on rename or move.
    print(f"Stored reference: {result['asset_id']}")
    print(f"Public ID:        {result['public_id']}")
    print(f"Dimensions:       {result['width']}x{result['height']} {result['format']}")
    print(f"Original URL:     {result['secure_url']}")

    optimized = cloudinary.CloudinaryImage(result["public_id"]).build_url(
        width=400,
        height=400,
        crop="fill",
        gravity="auto",
        fetch_format="auto",
        quality="auto",
        secure=True,
    )
    print(f"Optimized URL:    {optimized}")


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
