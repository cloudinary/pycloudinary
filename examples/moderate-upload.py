"""Upload an image into a manual moderation queue, list the queue, and approve it.

Moderation is stateful: an asset carries a status until a decision is recorded, and your
application should deliver only approved assets. A pending asset is still deliverable by
default - the status is metadata to gate on, not an access control. Blocking non-approved
assets is configured per product environment by Cloudinary support, not by an upload
parameter.

moderation="manual" needs no add-on subscription, so this runs on any account.

Prerequisites: set CLOUDINARY_URL in your environment (Console > Settings > API Keys).

Related:
- Task doc: cloudinary/docs/moderate-upload.md
- Plain uploads: examples/upload-image.py
"""
import cloudinary
import cloudinary.api
import cloudinary.exceptions
import cloudinary.uploader

# Configuration is read from CLOUDINARY_URL automatically.

SAMPLE_IMAGE = "https://res.cloudinary.com/demo/image/upload/sample.jpg"


def main() -> None:
    result = cloudinary.uploader.upload(
        SAMPLE_IMAGE,
        moderation="manual",
        folder="examples/user-uploads",
    )

    # The upload result carries a `moderation` list, not a flat `moderation_status`.
    public_id = result["public_id"]
    print(f"Uploaded:  {public_id}")
    print(f"Status:    {result['moderation'][0]['status']}")  # 'pending'
    print("Deliverable already - gate on the status in your own code.")

    pending = cloudinary.api.resources_by_moderation("manual", "pending", max_results=100)
    print(f"In the review queue: {len(pending['resources'])}")

    approved = cloudinary.api.update(public_id, moderation_status="approved")
    # resource() and update() responses expose both shapes.
    print(f"Status now: {approved['moderation_status']}")
    url = cloudinary.CloudinaryImage(public_id).build_url(
        width=400, crop="fill", fetch_format="auto", quality="auto", secure=True)
    print(f"URL:        {url}")


if __name__ == "__main__":
    try:
        main()
    except cloudinary.exceptions.Error as error:
        print(f"Moderation flow failed: {error}")
        raise SystemExit(1)
    except ValueError as error:
        print(f"Configuration error: {error}")
        print("Set CLOUDINARY_URL (Console > Settings > API Keys).")
        raise SystemExit(1)
