"""Generate the signature a browser needs to upload directly to Cloudinary.

Your server signs a set of upload parameters; the client posts the file plus that
signature. The api_secret never leaves your server, and the file never passes through it.

This script prints the payload a real endpoint would return as JSON, then performs the
client-side POST itself so you can see the whole round trip succeed.

Prerequisites: set CLOUDINARY_URL in your environment (Console > Settings > API Keys).

Related:
- Task doc: cloudinary/docs/sign-browser-upload.md
- Server-side uploads instead: examples/upload-image.py
- In Django, CloudinaryJsFileField does this for you: cloudinary/docs/use-with-django.md
"""
import json
import time
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen

import cloudinary
import cloudinary.exceptions
import cloudinary.utils

# Configuration is read from CLOUDINARY_URL automatically.


def signature_payload(folder: str = "examples/browser-uploads") -> dict:
    """What your signing endpoint should return to the browser."""
    config = cloudinary.config()

    # Every parameter signed here must be sent by the client, byte for byte.
    params_to_sign = {"timestamp": int(time.time()), "folder": folder}

    signature = cloudinary.utils.api_sign_request(params_to_sign, config.api_secret)

    payload = {
        "signature": signature,        # 40-character hex (SHA-1)
        "api_key": config.api_key,     # public, safe to send to the client
        "cloud_name": config.cloud_name,
        "upload_url": cloudinary.utils.cloudinary_api_url("upload", resource_type="image"),
    }
    payload.update(params_to_sign)
    return payload


def upload_as_client(payload: dict, file_url: str) -> dict:
    """What the browser does with that payload."""
    body = {
        "file": file_url,
        "api_key": payload["api_key"],
        "timestamp": payload["timestamp"],
        "folder": payload["folder"],
        "signature": payload["signature"],
    }
    response = urlopen(payload["upload_url"], urlencode(body).encode("utf-8"))
    return json.loads(response.read().decode("utf-8"))


def main() -> None:
    payload = signature_payload()
    print("Server returns to the browser:")
    print(json.dumps({k: v for k, v in payload.items() if k != "signature"}, indent=2))
    print(f"  signature: {payload['signature'][:8]}... ({len(payload['signature'])} chars)")

    print("\nClient uploads with it ...")
    result = upload_as_client(payload, "https://res.cloudinary.com/demo/image/upload/sample.jpg")
    print(f"  Uploaded: {result['public_id']}")
    print(f"  URL:      {result['secure_url']}")

    # Cloudinary signs its response so your server can trust the result.
    verified = cloudinary.utils.verify_api_response_signature(
        result["public_id"], result["version"], result["signature"]
    )
    print(f"  Response signature verified: {verified}")


if __name__ == "__main__":
    try:
        main()
    except HTTPError as error:
        detail = json.loads(error.read().decode("utf-8"))
        print(f"Upload rejected: {detail['error']['message']}")
        print("Signed and submitted parameters must match exactly.")
        raise SystemExit(1)
    except cloudinary.exceptions.Error as error:
        print(f"Signing failed: {error}")
        raise SystemExit(1)
    except ValueError as error:
        print(f"Configuration error: {error}")
        print("Set CLOUDINARY_URL (Console > Settings > API Keys).")
        raise SystemExit(1)
