@AGENTS.md

# CLAUDE.md — pycloudinary

## What this repo is

The official Cloudinary Python server-side SDK (`pip install cloudinary`, `import cloudinary`). One package covers plain Python and Django — upload, Admin/Search API, signed URLs, `CloudinaryField` model field, and `{% load cloudinary %}` template tags all ship here.

## Key constraints / gotchas

- **Two test suites, two runners.** Core tests: `python -m pytest test`. Django integration tests: `django-admin test django_tests` with `DJANGO_SETTINGS_MODULE=django_tests.settings`. The `tox` matrix pairs Python versions with Django versions — match it.
- **Tests require a real cloud.** Set `CLOUDINARY_URL=cloudinary://<api_key>:<api_secret>@<cloud_name>` before running any suite. CI derives credentials from `tools/get_test_cloud.sh`.
- **No `python_requires` floor.** `pip` will not block an unsupported interpreter; the supported range comes from classifiers and CI (Python 3.10–3.14, Django 4.2–6.0). Python 2.7 support is legacy, kept only in a `tox.ini` env, and flagged for removal in the next major.
- **Django ships in this package.** Do not look for or create a separate Django install. The `CloudinaryField` model field, forms, and template tags are all in `cloudinary/models.py`, `cloudinary/forms.py`, and the template tags module. The Django file-storage backend (`DEFAULT_FILE_STORAGE` / `STORAGES`) is the separate third-party `django-cloudinary-storage` project — not part of this package.
- **No lint step in CI.** `.github/workflows/test.yml` runs the tox test matrix only — there is no flake8/ruff/black config.
- **Signed uploads and Admin API calls require server-side secrets.** Never ship `api_secret` into a browser bundle.

## Verified build / test commands

```bash
pip install tox pytest

# Core (non-Django) tests:
python -m pytest test

# Django integration tests (requires Django installed):
DJANGO_SETTINGS_MODULE=django_tests.settings django-admin test -v2 django_tests

# Via tox to match CI exactly:
tox -e py313-core
tox -e py313-django51
```
