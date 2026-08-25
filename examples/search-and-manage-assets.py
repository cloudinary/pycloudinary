"""Search for assets, page through the results, then read and update one.

Search answers "find the assets matching X"; the Admin API answers "do something to this
asset". This script uses both.

Prerequisites: set CLOUDINARY_URL in your environment (Console > Settings > API Keys).
Run examples/upload-image.py first so there is something to find.

Related:
- Task doc: cloudinary/docs/search-and-manage-assets.md
- Typed fields you can search on: examples/use-structured-metadata.py
"""
import cloudinary
import cloudinary.api
import cloudinary.exceptions

# Configuration is read from CLOUDINARY_URL automatically.


def main() -> None:
    result = (
        cloudinary.Search()
        .expression("resource_type:image")
        .sort_by("created_at", "desc")
        .max_results(10)
        .with_field("tags")
        .execute()
    )

    print(f"Matches: {result['total_count']} (showing {len(result['resources'])})")
    for asset in result["resources"]:
        print(f"  {asset['asset_id']}  {asset['public_id']}  "
              f"{asset['bytes']} bytes  tags={asset.get('tags', [])}")

    if not result["resources"]:
        print("Nothing to manage yet - run examples/upload-image.py first.")
        return

    # Page with the cursor, never with total_count.
    pages = 1
    cursor = result.get("next_cursor")
    while cursor and pages < 3:
        page = cloudinary.Search().expression("resource_type:image").max_results(10) \
            .next_cursor(cursor).execute()
        pages += 1
        cursor = page.get("next_cursor")
    print(f"Walked {pages} page(s).")

    # Read through the Admin API by asset_id: it survives renames, public_id does not.
    asset_id = result["resources"][0]["asset_id"]
    asset = cloudinary.api.resource_by_asset_id(asset_id)
    print(f"\nDetails for {asset_id}:")
    print(f"  {asset.get('width')}x{asset.get('height')} {asset['format']}, "
          f"{len(asset.get('derived', []))} derived version(s)")

    # update() is public_id-only, so take it from the asset just fetched.
    updated = cloudinary.api.update(
        asset["public_id"],
        tags=["example", "reviewed"],
        context={"alt": "Updated by the pycloudinary example"},
    )
    print(f"  tags now: {updated.get('tags')}")


if __name__ == "__main__":
    try:
        main()
    except cloudinary.exceptions.Error as error:
        print(f"Search or update failed: {error}")
        raise SystemExit(1)
    except Exception as error:
        # Missing configuration surfaces as a bare Exception, not a ValueError.
        print(f"Configuration error: {error}")
        print("Set CLOUDINARY_URL (Console > Settings > API Keys).")
        raise SystemExit(1)
