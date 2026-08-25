"""Provision a Claimable Cloud - working credentials with no account and no signup.

Run this when you have no CLOUDINARY_URL. The credentials work immediately, so you can
upload, transform, and build the whole integration before anyone signs up. Media delivery
is restricted to the IPs in the response until a human claims the cloud.

Report the claim URL to the user: it is the only way to make the cloud permanent, and the
cloud (with its assets) is disabled at expires_at otherwise.

Prerequisites: none. This endpoint needs no authentication.

Related:
- Task doc: cloudinary/docs/get-credentials.md
- Then: examples/upload-image.py
"""
import json
from urllib.request import urlopen

import cloudinary.exceptions
from cloudinary.provisioning import create_cloud


def public_ip() -> str:
    """Cloudinary cannot allow-list a private address, so resolve the public one."""
    return urlopen("https://api.ipify.org").read().decode("utf-8").strip()


def main() -> None:
    try:
        cloud = create_cloud(
            agent_framework="pycloudinary-example",
            agent_llm_model="none",
            agent_goal="Try the Cloudinary Python SDK",
        )
    except cloudinary.exceptions.BadRequest as error:
        if "public IP" not in str(error):
            raise
        # Behind a VPN or proxy the request arrives from a private address.
        print("Retrying with an explicitly resolved public IP ...")
        cloud = create_cloud(
            delivery_ips=[public_ip()],
            agent_framework="pycloudinary-example",
            agent_llm_model="none",
            agent_goal="Try the Cloudinary Python SDK",
        )

    print(f"Cloud name:   {cloud['cloud_name']}")
    print(f"Delivery IPs: {cloud['delivery_ips']}")
    print(f"Expires at:   {cloud['expires_at']}")
    print("\nAdd this to your environment:")
    print(f"  export {cloud['api_environment_variable']}")
    print("\nGIVE THIS TO THE USER - claiming is the only way to keep the cloud:")
    print(f"  {cloud['claim_url']}")

    # Nothing writes .env for you when provisioning from Python.
    with open(".env", "a") as env_file:
        env_file.write(cloud["api_environment_variable"] + "\n")
        env_file.write("CLOUDINARY_CLOUD_CLAIM_URL=" + cloud["claim_url"] + "\n")
        env_file.write("CLOUDINARY_CLOUD_EXPIRES_AT=" + cloud["expires_at"] + "\n")
    print("\nWritten to ./.env")


if __name__ == "__main__":
    try:
        main()
    except cloudinary.exceptions.Error as error:
        print(f"Could not provision a cloud: {error}")
        print(json.dumps({"hint": "Clouds are rate-limited per IP; reuse the one you have."}))
        raise SystemExit(1)
