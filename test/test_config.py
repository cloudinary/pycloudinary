import os
import pytest
from unittest.mock import patch
import cloudinary
from cloudinary.provisioning import account_config

CLOUD_NAME = "test123"
API_KEY = "key"
API_SECRET = "secret"
OAUTH_TOKEN = "NTQ0NjJkZmQ5OTM2NDE1ZTZjNGZmZj17"
URL_WITH_OAUTH_TOKEN = "cloudinary://{}?oauth_token={}".format(CLOUD_NAME, OAUTH_TOKEN)
MOCKED_SETTINGS = {"api_secret": "secret_from_settings"}

def _clean_env():
    for key in os.environ.keys():
        if key.startswith("CLOUDINARY_"):
            if key != "CLOUDINARY_URL":
                del os.environ[key]

@pytest.fixture
def config_fixture():
    _clean_env()
    yield os.environ
    _clean_env()

def test_parse_cloudinary_url():
    config = cloudinary.config()
    parsed_url = config._parse_cloudinary_url(
        "cloudinary://key:secret@test123?foo[bar]=value"
    )
    config._setup_from_parsed_url(parsed_url)
    foo = config.__dict__.get("foo")
    assert foo is not None
    assert foo.get("bar") == "value"


def test_cloudinary_url_valid_scheme():
    config = cloudinary.config()
    cloudinary_urls = [
        "cloudinary://123456789012345:ALKJdjklLJAjhkKJ45hBK92baj3@test"
        "CLouDiNaRY://123456789012345:ALKJdjklLJAjhkKJ45hBK92baj3@test"
    ]
    for cloudinary_url in cloudinary_urls:
        parsed_url = config._parse_cloudinary_url(cloudinary_url)
        config._setup_from_parsed_url(parsed_url)


def test_cloudinary_url_invalid_scheme():
    config = cloudinary.config()
    cloudinary_urls = [
        "CLOUDINARY_URL=cloudinary://123456789012345:ALKJdjklLJAjhkKJ45hBK92baj3@test",
        "https://123456789012345:ALKJdjklLJAjhkKJ45hBK92baj3@test",
        "://123456789012345:ALKJdjklLJAjhkKJ45hBK92baj3@test",
        "https://123456789012345:ALKJdjklLJAjhkKJ45hBK92baj3@test?cloudinary=foo",
        " ",
    ]
    for cloudinary_url in cloudinary_urls:
        with pytest.raises(ValueError) as excinfo:
            parsed_url = config._parse_cloudinary_url(cloudinary_url)
            config._setup_from_parsed_url(parsed_url)
    assert str(excinfo.value) == "Invalid CLOUDINARY_URL scheme. Expecting to start with 'cloudinary://'"


def test_parse_cloudinary_account_url():
    config = account_config()
    parsed_url = config._parse_cloudinary_url(
        "account://key:secret@test123?foo[bar]=value"
    )
    config._setup_from_parsed_url(parsed_url)
    foo = config.__dict__.get("foo")
    assert foo is not None
    assert foo.get("bar") == "value"


def test_cloudinary_account_url_valid_scheme():
    config = account_config()
    cloudinary_account_urls = [
        "account://123456789012345:ALKJdjklLJAjhkKJ45hBK92baj3@test"
        "aCCouNT://123456789012345:ALKJdjklLJAjhkKJ45hBK92baj3@test"
    ]
    for cloudinary_account_url in cloudinary_account_urls:
        parsed_url = config._parse_cloudinary_url(cloudinary_account_url)
        config._setup_from_parsed_url(parsed_url)


def test_cloudinary_account_url_invalid_scheme():
    config = account_config()
    cloudinary_account_urls = [
        "CLOUDINARY__ACCOUNT_URL=account://123456789012345:ALKJdjklLJAjhkKJ45hBK92baj3@test",
        "https://123456789012345:ALKJdjklLJAjhkKJ45hBK92baj3@test",
        "://123456789012345:ALKJdjklLJAjhkKJ45hBK92baj3@test",
        "https://123456789012345:ALKJdjklLJAjhkKJ45hBK92baj3@test?account=foo" " ",
    ]
    for cloudinary_account_url in cloudinary_account_urls:
        with pytest.raises(ValueError) as excinfo:
            parsed_url = config._parse_cloudinary_url(cloudinary_account_url)
            config._setup_from_parsed_url(parsed_url)
    assert str(excinfo.value) == "Invalid CLOUDINARY_ACCOUNT_URL scheme. URL should begin with 'account://'"


def test_support_CLOUDINARY_prefixed_environment_variables(config_fixture):
    os.environ["CLOUDINARY_CLOUD_NAME"] = "c"
    os.environ["CLOUDINARY_API_KEY"] = "k"
    os.environ["CLOUDINARY_API_SECRET"] = "s"
    os.environ["CLOUDINARY_SECURE_DISTRIBUTION"] = "sd"
    os.environ["CLOUDINARY_PRIVATE_CDN"] = "false"
    os.environ["CLOUDINARY_SECURE"] = "true"

    config = cloudinary.Config()
    assert config.cloud_name == "c"
    assert config.api_key == "k"
    assert config.api_secret == "s"
    assert config.secure_distribution == "sd"
    assert not config.private_cdn
    assert config.secure


def test_overwrites_only_existing_keys_from_environment(config_fixture):
    os.environ["CLOUDINARY_CLOUD_NAME"] = "c"
    os.environ["CLOUDINARY_API_KEY"] = "key_from_env"

    with patch("cloudinary.import_django_settings", return_value=MOCKED_SETTINGS):
        config = cloudinary.Config()
        assert config.cloud_name == "c"
        assert config.api_key == "key_from_env"
        assert config.api_secret == "secret_from_settings"


def test_config_from_url_without_key_and_secret_but_with_oauth_token():
    config = cloudinary.config()
    parsed_url = config._parse_cloudinary_url(URL_WITH_OAUTH_TOKEN)
    config._setup_from_parsed_url(parsed_url)
    assert config.cloud_name == CLOUD_NAME
    assert config.oauth_token == OAUTH_TOKEN
    assert config.api_key is None
    assert config.api_secret is None


def test_config_from_url_with_key_and_secret_and_oauth_token():
    config = cloudinary.config()
    parsed_url = config._parse_cloudinary_url(
        "cloudinary://{}:{}@test123?oauth_token={}".format(
            API_KEY, API_SECRET, OAUTH_TOKEN
        )
    )
    config._setup_from_parsed_url(parsed_url)
    assert config.cloud_name == CLOUD_NAME
    assert config.oauth_token == OAUTH_TOKEN
    assert config.api_key == API_KEY
    assert config.api_secret == API_SECRET
