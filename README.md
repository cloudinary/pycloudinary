# Cloudinary Python SDK

[![Tests](https://github.com/cloudinary/pycloudinary/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/cloudinary/pycloudinary/actions/workflows/test.yml)
[![PyPI version](https://img.shields.io/pypi/v/cloudinary.svg)](https://pypi.org/project/cloudinary/)
[![PyPI Python versions](https://img.shields.io/pypi/pyversions/cloudinary.svg)](https://pypi.org/project/cloudinary/)
[![PyPI license](https://img.shields.io/pypi/l/cloudinary.svg)](https://pypi.org/project/cloudinary/)

The `cloudinary` package is the server-side Cloudinary SDK for Python. Use it in a backend or build step to upload assets, build transformation and delivery URLs, and call the Admin API. It holds the API secret, so it handles the operations that can't run in a browser: signed uploads, signed delivery URLs, and asset administration. The same package covers plain Python and Django — the `CloudinaryField` model field, forms, and `{% load cloudinary %}` template tags ship inside it. The package and import name are both `cloudinary`. The current release (1.45.0) is tested on Python 3.10 through 3.14 and Django 4.2 through 6.0.

## Installation

```bash
pip install cloudinary
```

## Configuration

The SDK reads credentials automatically from the `CLOUDINARY_URL` environment variable on import:

```bash
export CLOUDINARY_URL=cloudinary://<API_KEY>:<API_SECRET>@<CLOUD_NAME>
```

To set them in code instead, call `cloudinary.config()`:

```python
import cloudinary

cloudinary.config(
    cloud_name="my_cloud_name",
    api_key="my_key",
    api_secret="my_secret",
    secure=True,  # emit https:// delivery URLs
)
```

Keep the API secret on the server. Don't put it in client-side code or commit it to version control.

## Quick examples

### Upload a file

`cloudinary.uploader.upload(file, **options)` accepts a local path, a remote URL, a data URI, a file object, or raw bytes as its first argument, and returns a dict of the uploaded asset's metadata, including `public_id` and `secure_url`:

```python
import cloudinary.uploader
# Credentials come from CLOUDINARY_URL in the environment.

result = cloudinary.uploader.upload(
    "my_picture.jpg",
    public_id="cms/hero",  # optional: where the asset lives in your media library
)
print(result["public_id"], result["secure_url"])
```

### Build and optimize a delivery URL

`cloudinary.utils.cloudinary_url(source, **options)` is synchronous and makes no network call. It returns a `(url, options)` tuple whose first element is the delivery URL string. This one resizes to a 100x150 fill crop and lets Cloudinary pick the format and quality for the requesting browser (`f_auto`, `q_auto`):

```python
import cloudinary.utils

url, options = cloudinary.utils.cloudinary_url(
    "sample.jpg",
    width=100, height=150, crop="fill",
    fetch_format="auto", quality="auto",
    secure=True,  # emit an https:// delivery URL
)
print(url)
# https://res.cloudinary.com/demo/image/upload/c_fill,f_auto,h_150,q_auto,w_100/sample.jpg
```

### Retrieve asset details

`cloudinary.api.resource(public_id, **options)` takes a public ID and returns the asset's metadata, including its dimensions, format, and `secure_url`:

```python
import cloudinary.api
# Credentials come from CLOUDINARY_URL in the environment.

asset = cloudinary.api.resource("sample")
print(asset["format"], asset["width"], asset["height"], asset["secure_url"])
```

## For AI agents

`cloudinary` is the Python server-side SDK, and it's also the Django SDK — the `CloudinaryField` model field (`cloudinary.models`), forms (`cloudinary.forms`), and `{% load cloudinary %}` template tags ship in this one package, so there's no separate Django SDK to install. Choose it for backend upload, asset administration, the Search API, and signed URL or tag generation, where the API secret stays private. For tasks it doesn't cover, choose a different package:

| Task | Package |
|---|---|
| Build delivery URLs in the browser | [`@cloudinary/url-gen`](https://github.com/cloudinary/js-url-gen) |
| Wire Cloudinary in as Django's `DEFAULT_FILE_STORAGE` / `STORAGES` backend | [`django-cloudinary-storage`](https://github.com/klis87/django-cloudinary-storage) (third-party) |
| Run Cloudinary operations as agent tools | [Cloudinary MCP servers](https://github.com/cloudinary/mcp-servers) |

The Django file-storage backend is the only Django piece this package doesn't ship — `CloudinaryField` covers the common case without it.

## Links

- [Python SDK guide](https://cloudinary.com/documentation/django_integration)
- [Upload](https://cloudinary.com/documentation/django_image_and_video_upload)
- [Asset administration (Admin API)](https://cloudinary.com/documentation/django_asset_administration)
- [Image transformations](https://cloudinary.com/documentation/django_image_manipulation)
- [Transformation and API references](https://cloudinary.com/documentation/cloudinary_references)
- [Documentation llms.txt index](https://cloudinary.com/documentation/llms.txt)
- [Package on PyPI](https://pypi.org/project/cloudinary/)

Released under the MIT license.
