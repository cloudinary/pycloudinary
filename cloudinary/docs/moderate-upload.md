# Moderate an upload

## When to use

Holding user-generated content back from delivery until it is approved — either by a
person or by an automated add-on.

An asset with a pending moderation status is uploaded and stored, but its delivery URL
returns 404 until it is approved. That is the mechanism: no separate quarantine bucket, no
second upload.

For platform-wide moderation with review queues and rules, see
[Cloudinary Moderation](https://cloudinary.com/documentation/cloudinary_moderation.md) —
distinct from the per-asset flag this SDK sets.

## Complete flow (manual review queue)

```python
import cloudinary
import cloudinary.api
import cloudinary.uploader

# Configuration is read from CLOUDINARY_URL automatically.


def main():
    result = cloudinary.uploader.upload(
        "https://res.cloudinary.com/demo/image/upload/sample.jpg",
        moderation="manual",              # hold for review
        folder="user-uploads",
    )

    # The upload result carries a `moderation` list, not a `moderation_status` key.
    print(result["moderation"])          # [{'kind': 'manual', 'status': 'pending'}]
    public_id = result["public_id"]

    # Later: list what is waiting for review.
    pending = cloudinary.api.resources_by_moderation("manual", "pending", max_results=100)
    print(len(pending["resources"]))

    # Approve it (or "rejected" to keep it dark).
    approved = cloudinary.api.update(public_id, moderation_status="approved")
    print(approved["moderation_status"])  # 'approved' — now deliverable
    print(approved["moderation"])         # [{'kind': 'manual', 'status': 'approved', 'updated_at': ...}]

    return approved


if __name__ == "__main__":
    try:
        main()
    except cloudinary.exceptions.Error as error:
        print("Moderation flow failed: {0}".format(error))
        raise SystemExit(1)
```

## Result fields to keep

Store `asset_id` and `public_id` alongside your own review record.

Which field holds the status depends on the call: the **upload** result exposes only the
`moderation` list (`[{"kind": "manual", "status": "pending"}]`), while
`cloudinary.api.resource()` and `cloudinary.api.update()` return both `moderation` and a
flat `moderation_status`. Read `result["moderation"][0]["status"]` if you want one
expression that works everywhere.

The three statuses are `pending`, `approved`, and `rejected`. Only `approved` delivers.

## Automated moderation

Replace `moderation="manual"` with an add-on. These are paid and must be enabled on the
account first:

```python
cloudinary.uploader.upload(source, moderation="aws_rek")            # images
cloudinary.uploader.upload(source, moderation="google_video_moderation",
                           resource_type="video")                    # video
cloudinary.uploader.upload(source, moderation="perception_point")    # malware
```

Automated moderation is asynchronous: the upload returns `pending` and the verdict lands
seconds to minutes later. Do not block on it — set `notification_url` and react to the
webhook, or poll `cloudinary.api.resource(public_id)`.

Assert on shape, not on verdicts. Model output varies between runs and versions, so check
that a `moderation` entry exists with a known status value rather than expecting a
specific score.

## Combining moderation with tagging

Moderation answers "may this be shown"; the analysis add-ons answer "what is in it". They
compose in one call:

```python
cloudinary.uploader.upload(
    source,
    moderation="aws_rek",
    categorization="google_tagging",
    auto_tagging=0.7,          # apply tags above this confidence
    notification_url="https://example.com/cloudinary-hook",
)
```

## Troubleshooting

- The URL 404s right after upload — that is moderation working. Approve the asset, or
  check `moderation_status`.
- `You don't have an active subscription for <add-on>` (raised as `RateLimited`, not a
  permission error) — the named add-on is not enabled on this account.
  `moderation="manual"` needs no subscription and is the way to test the flow.
- `moderation_status` stays `pending` forever with an automated kind — the add-on is
  queued or failed; check the `moderation` entry for an error, and confirm the add-on
  supports the resource type.
- `Illegal moderation status: <value>` on update — the accepted values are `approved`
  and `rejected`.
- `resources_by_moderation` returns nothing — the `kind` argument must match the
  moderation used at upload (`manual`, `aws_rek`, ...), not the status.
- Rejected assets still occupy storage. Delete them with `cloudinary.uploader.destroy()`
  if you do not need an audit trail.

## Related

- Runnable example: `examples/moderate-upload.py`
- [Upload an image](upload-image.md)
- [Search and manage assets](search-and-manage-assets.md) — finding and deleting what you
  moderated.
- [Moderation add-ons](https://cloudinary.com/documentation/moderate_assets.md)
