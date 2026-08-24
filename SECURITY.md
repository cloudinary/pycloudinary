# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 1.x     | Yes       |

## Reporting a vulnerability

Report security issues privately through
[GitHub private vulnerability reporting](https://github.com/cloudinary/pycloudinary/security/advisories/new).

If you cannot use GitHub, open a ticket at
[support.cloudinary.com](https://support.cloudinary.com) and mark the ticket as a
security issue.

Use these private channels for anything security-sensitive; public GitHub issues are
for regular bugs and feature requests.

## What to include in a report

- The affected package version and your Python version.
- A minimal reproduction or proof of concept.
- The impact you believe it has — for example: credential exposure, signature
  bypass, request forgery.
- Any suggested remediation.

## Response and disclosure process

- We acknowledge reports and keep you informed while we investigate.
- Fixes ship as patched versions, with a changelog entry noting the security-relevant
  change without exploit detail before users can upgrade.
- We ask for reasonable time to release a fix before public disclosure.

## Security guidance for SDK users

- Your `api_secret` belongs in server-side code only. Never ship it in a browser
  bundle, mobile app, or public repository.
- Configure the SDK from the `CLOUDINARY_URL` environment variable rather than
  hardcoding credentials.
- Sign browser and mobile uploads on your server — see
  [cloudinary/docs/sign-browser-upload.md](cloudinary/docs/sign-browser-upload.md).
- If you use unsigned uploads, restrict the upload preset deliberately: allowed
  formats, size limits, and a fixed folder. See
  [upload presets](https://cloudinary.com/documentation/upload_presets)
  ([md](https://cloudinary.com/documentation/upload_presets.md)).
- Platform-level security options are documented in
  [Cloudinary security](https://cloudinary.com/documentation/control_access_to_media)
  ([md](https://cloudinary.com/documentation/control_access_to_media.md)).
