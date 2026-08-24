# Cloudinary Python SDK

Upload, transform, optimize, and manage images and videos with Cloudinary from Python or Django — the `cloudinary` package on PyPI.

[![Tests](https://github.com/cloudinary/pycloudinary/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/cloudinary/pycloudinary/actions/workflows/test.yml)
[![PyPI](https://img.shields.io/pypi/v/cloudinary.svg)](https://pypi.org/project/cloudinary/)
[![Downloads](https://img.shields.io/pypi/dm/cloudinary.svg)](https://pypi.org/project/cloudinary/)
[![License](https://img.shields.io/pypi/l/cloudinary.svg)](LICENSE)

## Install

```bash
pip install cloudinary
```

## Quick start

Set your API environment variable (Console > Settings > API Keys):

```bash
export CLOUDINARY_URL=cloudinary://<api_key>:<api_secret>@<cloud_name>
```

Upload an image and get an optimized delivery URL:

```python
import cloudinary
import cloudinary.uploader  # cloudinary.uploader must be imported explicitly

# Configuration is read from CLOUDINARY_URL automatically.


def main():
    # Upload a remote image (a local file path works the same way)
    result = cloudinary.uploader.upload(
        "https://res.cloudinary.com/demo/image/upload/sample.jpg",
        public_id="quickstart-sample",
    )
    print("Uploaded: {0}".format(result["public_id"]))

    # Build a 400x400 auto-cropped URL with automatic format and quality
    url = cloudinary.CloudinaryImage(result["public_id"]).build_url(
        width=400,
        height=400,
        crop="fill",
        gravity="auto",
        fetch_format="auto",
        quality="auto",
        secure=True,
    )
    print("Optimized URL: {0}".format(url))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("Quick start failed: {0}".format(error))
        print("Check that CLOUDINARY_URL is set (Console > Settings > API Keys).")
        raise SystemExit(1)
```

Save as `quickstart.py` and run `python quickstart.py`. [Create a free account](https://cloudinary.com/users/register_free) if you don't have one — or call `cloudinary.provisioning.create_cloud()` to [provision one without signing up](cloudinary/docs/get-credentials.md).

## Common tasks

- [Get Cloudinary credentials](cloudinary/docs/get-credentials.md)
- [Upload an image](cloudinary/docs/upload-image.md)
- [Upload a large video](cloudinary/docs/upload-large-video.md)
- [Sign a browser upload](cloudinary/docs/sign-browser-upload.md)
- [Transform and deliver an image](cloudinary/docs/transform-and-deliver-image.md)
- [Transform and deliver a video](cloudinary/docs/transform-and-deliver-video.md)
- [Search and manage assets](cloudinary/docs/search-and-manage-assets.md)
- [Moderate an upload](cloudinary/docs/moderate-upload.md)
- [Use structured metadata](cloudinary/docs/use-structured-metadata.md)
- [Use with Django](cloudinary/docs/use-with-django.md)
- [Troubleshoot errors](cloudinary/docs/troubleshoot-errors.md)

Runnable versions live in [`examples/`](examples/) — each is a complete file you can run directly.

## When to use this SDK

Use this package in **Python server-side code**, including Django: uploads, signed
operations, asset administration, search, moderation, and delivery URL generation.

For other jobs, better-fitting tools exist:

- Browser or frontend framework rendering: the [frontend SDKs](https://cloudinary.com/documentation/frontend_sdks) ([md](https://cloudinary.com/documentation/frontend_sdks.md)).
- Complete in-browser upload UI: [Upload Widget](https://cloudinary.com/documentation/upload_widget) ([md](https://cloudinary.com/documentation/upload_widget.md)).
- Text-to-image generation and image-to-video: [platform APIs](https://cloudinary.com/documentation/image_generation_addon) ([md](https://cloudinary.com/documentation/image_generation_addon.md)), not wrapped by this package.
- Multi-step media workflow automation: [MediaFlows](https://cloudinary.com/documentation/mediaflows_user_guide) ([md](https://cloudinary.com/documentation/mediaflows_user_guide.md)).
- Interactive agent-driven asset operations: [Cloudinary MCP servers and Skills](https://cloudinary.com/documentation/cloudinary_llm_mcp) ([md](https://cloudinary.com/documentation/cloudinary_llm_mcp.md)).

The full capability map — plus the Skills, MCP servers, and CLI worth setting up first —
is in [cloudinary/docs/platform-capabilities.md](cloudinary/docs/platform-capabilities.md).

## Status and compatibility

Stable, actively maintained. See [CHANGELOG.md](CHANGELOG.md).

| SDK version | Python | Django |
|-------------|--------|--------|
| 1.x | 3.10 – 3.14 | 4.2, 5.0, 5.1, 5.2, 6.0 |

The table lists what CI tests on every commit. Older Python and Django releases are
supported on a best-effort basis.

## Documentation

- [Bundled task docs](cloudinary/docs/README.md) — ship inside the package, version-matched.
- [Python and Django SDK guide](https://cloudinary.com/documentation/django_integration) — the full documentation ([md](https://cloudinary.com/documentation/django_integration.md)).
- [Python quick start](https://cloudinary.com/documentation/python_quickstart) — a short end-to-end walkthrough ([md](https://cloudinary.com/documentation/python_quickstart.md)).
- [Transformation and REST API references](https://cloudinary.com/documentation/cloudinary_references) — syntax and examples for all SDKs ([md](https://cloudinary.com/documentation/cloudinary_references.md)).

Documentation links in this README point at the browsable HTML page, with an `(md)`
companion link that returns the same page as raw Markdown. Inside `cloudinary/docs/` and
`examples/` the links are Markdown-only, since those files are written to be read by
coding agents. Either form works for any page: add `.md` for Markdown, drop it for HTML.

## For AI coding agents

- Contributing to this repo: read [AGENTS.md](AGENTS.md).
- Using the installed package: the Markdown docs in the installed package's
  `cloudinary/docs/` directory match your installed version and are the source of truth.
  Locate them with
  `python -c "import cloudinary, pathlib; print(pathlib.Path(cloudinary.__file__).parent / 'docs')"`,
  and start with [platform-capabilities](cloudinary/docs/platform-capabilities.md) before
  assuming a feature exists.

## Support

- SDK bugs and feature requests: [GitHub issues](https://github.com/cloudinary/pycloudinary/issues)
- Account and platform questions: [Cloudinary support](https://support.cloudinary.com)
- Sample projects: [`samples/`](samples/) and the
  [Django Photo Album](https://github.com/cloudinary/cloudinary-django-sample)
- Contributing: [CONTRIBUTING.md](CONTRIBUTING.md)

More resources: [Cloudinary Academy](https://training.cloudinary.com/) for courses,
[code explorers and feature demos](https://cloudinary.com/documentation/code_explorers_demos_index),
and the [Cloudinary roadmap](https://cloudinary.com/roadmap).

## Security

See [SECURITY.md](SECURITY.md) for private vulnerability reporting. Keep your
`api_secret` in server-side code; for client uploads, use the server-signed pattern in
[Sign a browser upload](cloudinary/docs/sign-browser-upload.md).

## License

Released under the MIT license — see [LICENSE](LICENSE). Copyright (c) Cloudinary Ltd.
