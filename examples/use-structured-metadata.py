"""Define structured metadata fields, set values on an asset, and search on them.

Structured metadata is typed and validated, unlike tags (a flat list) or context
(free-form key/value pairs). Fields are defined once on the account, then set per asset.

Prerequisites: set CLOUDINARY_URL in your environment (Console > Settings > API Keys).

Related:
- Task doc: cloudinary/docs/use-structured-metadata.md
- Searching: examples/search-and-manage-assets.py
"""
import time

import cloudinary
import cloudinary.api
import cloudinary.exceptions
import cloudinary.uploader

# Configuration is read from CLOUDINARY_URL automatically.

SAMPLE_IMAGE = "https://res.cloudinary.com/demo/image/upload/sample.jpg"


def ensure_field(definition: dict) -> None:
    """Define a field, tolerating one that already exists."""
    try:
        cloudinary.api.add_metadata_field(definition)
        print(f"  defined {definition['external_id']}")
    except cloudinary.exceptions.BadRequest as error:
        if "already exists" not in str(error):
            raise
        print(f"  {definition['external_id']} already defined")


def main() -> None:
    print("Defining fields:")
    ensure_field({"external_id": "example_sku", "label": "Example SKU", "type": "string"})
    ensure_field({
        "external_id": "example_category",
        "label": "Example Category",
        "type": "enum",
        # The value you assign is the option's external_id, not its display value.
        "datasource": {"values": [{"external_id": "bags", "value": "Bags"},
                                  {"external_id": "shoes", "value": "Shoes"}]},
    })

    result = cloudinary.uploader.upload(
        SAMPLE_IMAGE,
        public_id="examples/metadata-sample",
        metadata={"example_sku": "BAG-001"},
    )
    print(f"\nUploaded with metadata: {result['metadata']}")

    cloudinary.uploader.update_metadata(
        {"example_sku": "BAG-002", "example_category": "bags"},
        [result["public_id"]],
    )
    updated = cloudinary.api.resource_by_asset_id(result["asset_id"])["metadata"]
    print(f"Updated metadata:       {updated}")

    # The search index lags a write by a few seconds.
    time.sleep(5)
    found = (
        cloudinary.Search()
        .expression('metadata.example_sku="BAG-002"')
        .with_field("metadata")
        .execute()
    )
    print(f"\nSearch matches: {found['total_count']}")
    for asset in found["resources"]:
        print(f"  {asset['public_id']} -> {asset.get('metadata')}")


if __name__ == "__main__":
    try:
        main()
    except cloudinary.exceptions.Error as error:
        print(f"Metadata flow failed: {error}")
        raise SystemExit(1)
    except Exception as error:
        # Missing configuration surfaces as a bare Exception, not a ValueError.
        print(f"Configuration error: {error}")
        print("Set CLOUDINARY_URL (Console > Settings > API Keys).")
        raise SystemExit(1)
