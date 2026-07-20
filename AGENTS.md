# AGENTS.md — pycloudinary

## What this package is (one line)
Official Cloudinary Python server-side SDK (PyPI `cloudinary`, imported as `import cloudinary`): upload assets, build transformation/delivery URLs, and call the Admin API from a backend — and it ships the Django integration in the same package.

## When to use this / when NOT to use this
- **Use this when:** you are in a Python server runtime (Django, Flask, FastAPI, Celery, serverless, scripts) and need to upload assets, administer assets via the Admin API, or generate signed delivery URLs/tags where the `api_secret` must stay private.
- **Do NOT use this when:** the code runs in a **browser/frontend bundle** — use [`@cloudinary/url-gen`](https://github.com/cloudinary/js-url-gen) there (no secret exposed); or you want the no-code/autonomous-agent path — use the Cloudinary MCP server.
- **Sibling packages:** there is **no separate Django package** — the `CloudinaryField` model field, forms, and `{% load cloudinary %}` template tags all live in this one package (`cloudinary.models` / `cloudinary.forms`). (Note: this package does **not** ship a Django file-storage backend; that's the separate third-party `django-cloudinary-storage` project.) `@cloudinary/url-gen` = browser URL builder, a different (JS) repo. Rule of thumb: server → this package; browser → not this package.

## Setup
```bash
pip install cloudinary
```
Required configuration / credentials (the SDK reads `CLOUDINARY_URL` automatically):
```bash
export CLOUDINARY_URL=cloudinary://<api_key>:<api_secret>@<cloud_name>
```

## Minimal runnable example
```python
import cloudinary
import cloudinary.uploader
import cloudinary.utils

# Config is read from the CLOUDINARY_URL env var; no explicit cloudinary.config() needed.

# Upload a local file
result = cloudinary.uploader.upload("my_picture.jpg")
public_id = result["public_id"]

# Build a 100x150 fill-crop delivery URL for it
url, options = cloudinary.utils.cloudinary_url(public_id, width=100, height=150, crop="fill")
print(url)
```

## Build / test commands (run these after editing)
CI is driven by `tox` (see `tox.ini`); run the matching env locally after any change to `cloudinary/`.
```bash
pip install tox pytest

# Core (non-Django) tests — what tox runs as the *-core envs:
python -m pytest test

# Or via tox, e.g. core on the active Python:
tox -e py313-core

# Django integration tests (modern Django; uses django_tests/settings.py):
DJANGO_SETTINGS_MODULE=django_tests.settings django-admin test -v2 django_tests
# Or via tox:
tox -e py313-django51
```
Tests hit a real cloud — set `CLOUDINARY_URL` first (CI derives it from `tools/get_test_cloud.sh`). CI (`.github/workflows/test.yml`) runs only the `tox` test matrix — there is no lint step (no flake8/ruff/black config in the repo).

## Conventions & gotchas
- **Django ships in this package.** Do not look for or create a separate Django install. Django code lives under `cloudinary/models.py`, `cloudinary/forms.py`, and the template tags; its tests live in `django_tests/` with `DJANGO_SETTINGS_MODULE=django_tests.settings`.
- **Two test suites, two runners.** Core tests use `pytest` (`python -m pytest test`); Django tests use the Django test runner (`django-admin test django_tests`), not pytest. The `tox` matrix pairs Python versions with Django versions — match it.
- **Signed uploads and Admin calls require server-side secrets** — never ship `api_secret` into a browser bundle. That is the entire reason this SDK is server-only.
- **Python version floor is implicit.** Neither `setup.py` nor `pyproject.toml` declares an explicit `python_requires`; supported versions come only from the classifiers (Python 2.7 and 3.10–3.14). CI (`.github/workflows/test.yml`) tests 3.10–3.14 against Django 4.2–6.0; Python 2.7 / Django 1.11 support is legacy, kept only in a `tox.ini` env and flagged in `setup.py` for removal in the next major. Don't assume `pip` will block an unsupported interpreter.
- **Legacy 2.7 path in setup.py.** `setup.py` branches on `version_info[0] >= 3` and only hard-codes metadata under Python 2; on Python 3 it calls bare `setup()` reading `pyproject.toml`. Edit the right place.
- Runtime deps are intentionally minimal: `six`, `urllib3>=1.26.5`, `certifi`.

## Canonical docs (leave the repo for depth)
- Python SDK / Django guide: https://cloudinary.com/documentation/django_integration
- Upload: https://cloudinary.com/documentation/django_image_and_video_upload
- Admin API (asset administration): https://cloudinary.com/documentation/django_asset_administration
- Transformation & API reference: https://cloudinary.com/documentation/cloudinary_references
- MCP server (agent/no-code path): https://github.com/cloudinary/mcp-servers

## Agent / MCP note
If this capability is also exposed via the Cloudinary MCP servers, prefer the MCP tool for autonomous task execution and use this SDK for code generation. See cloudinary/mcp-servers.

## Commit / PR conventions
- Ensure both relevant test suites run locally (core via pytest, Django via the Django runner) and pass in CI before opening a PR.
- See `CONTRIBUTING.md` in the repo root.
