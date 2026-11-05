"""Group assets into a collection, share it as a public page, then clean up.

A collection references assets without moving or copying them. A public page is a
shareable link to the collection.

Prerequisites: set CLOUDINARY_URL in your environment (Console > Settings > API Keys).
Collections must be available on your plan; the Assets Free plan allows 3.

Related:
- Task doc: cloudinary/docs/organize-and-share-collections.md
- Finding asset IDs to add: examples/search-and-manage-assets.py
"""
import time

import cloudinary
import cloudinary.exceptions
import cloudinary.uploader
from cloudinary import collections  # must be imported explicitly

# Configuration is read from CLOUDINARY_URL automatically.

SAMPLE_IMAGE = "https://res.cloudinary.com/demo/image/upload/sample.jpg"


def wait_for_assets(collection_id: str, expected: int) -> list:
    """Poll until the collection lists the expected number of assets."""
    for _ in range(10):
        assets = collections.collection_assets(collection_id)["data"]
        if len(assets) == expected:
            return assets
        time.sleep(2)
    raise TimeoutError(f"Collection did not reach {expected} asset(s)")


def main() -> None:
    asset = cloudinary.uploader.upload(SAMPLE_IMAGE, tags=["collections-example"])
    print(f"Uploaded {asset['public_id']} (asset_id {asset['asset_id']})")

    collection = collections.create_collection(
        "Collections example",
        description="Created by examples/organize-and-share-collections.py",
    )["data"]
    print(f"Created {collection['type']} collection {collection['id']}")

    try:
        # Assets are added by asset_id, not public_id.
        collections.add_collection_assets(collection["id"], [asset["asset_id"]])
        for item in wait_for_assets(collection["id"], 1):
            print(f"  contains {item['public_id']}  {item['secure_url']}")

        page = collections.create_collection_public_page(collection["id"], name="Example page")["data"]
        print(f"Public page: {page['url']}")

        collections.update_collection_public_page(collection["id"], page["id"],
                                                  show_download_original_option=False)
        pages = collections.collection_public_pages(collection["id"])["data"]
        print(f"Collection has {len(pages)} public page(s)")

        collections.delete_collection_public_page(collection["id"], page["id"])
        print("Unpublished the page")
    finally:
        collections.delete_collection(collection["id"])
        cloudinary.uploader.destroy(asset["public_id"])
        print("Deleted the collection and the sample asset")


if __name__ == "__main__":
    try:
        main()
    except cloudinary.exceptions.Error as error:
        print(f"Collections call failed: {error}")
        raise SystemExit(1)
    except Exception as error:
        # Missing configuration surfaces as a bare Exception, not a ValueError.
        print(f"Error: {error}")
        raise SystemExit(1)
