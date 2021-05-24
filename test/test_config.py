import os
from unittest import TestCase

from mock import mock

import cloudinary
from cloudinary.provisioning import account_config


MOCKED_SETTINGS = {
    'api_secret': 'secret_from_settings'
}


def _clean_env():
    for key in os.environ.keys():
        if key.startswith("CLOUDINARY_"):
            if key != "CLOUDINARY_URL":
                del os.environ[key]


class TestConfig(TestCase):
    def setUp(self):
        self._environ_backup = os.environ.copy()
        _clean_env()

    def tearDown(self):
        _clean_env()

        for key, val in self._environ_backup.items():
            os.environ[key] = val

    def test_parse_cloudinary_url(self):
        config = cloudinary.config()
        parsed_url = config._parse_cloudinary_url('cloudinary://key:secret@test123?foo[bar]=value')
        config._setup_from_parsed_url(parsed_url)
        foo = config.__dict__.get('foo')
        self.assertIsNotNone(foo)
        self.assertEqual(foo.get('bar'), 'value')

    def test_cloudinary_url_valid_scheme(self):
        config = cloudinary.config()
        cloudinary_urls = [
            'cloudinary://123456789012345:ALKJdjklLJAjhkKJ45hBK92baj3@test'
            'CLouDiNaRY://123456789012345:ALKJdjklLJAjhkKJ45hBK92baj3@test'
        ]
        for cloudinary_url in cloudinary_urls:
            parsed_url = config._parse_cloudinary_url(cloudinary_url)
            config._setup_from_parsed_url(parsed_url)

    def test_cloudinary_url_invalid_scheme(self):
        config = cloudinary.config()
        cloudinary_urls = [
            'CLOUDINARY_URL=cloudinary://123456789012345:ALKJdjklLJAjhkKJ45hBK92baj3@test',
            'https://123456789012345:ALKJdjklLJAjhkKJ45hBK92baj3@test',
            '://123456789012345:ALKJdjklLJAjhkKJ45hBK92baj3@test',
            'https://123456789012345:ALKJdjklLJAjhkKJ45hBK92baj3@test?cloudinary=foo',
            ' '
        ]
        for cloudinary_url in cloudinary_urls:
            with self.assertRaises(ValueError):
                parsed_url = config._parse_cloudinary_url(cloudinary_url)
                config._setup_from_parsed_url(parsed_url)

    def test_parse_cloudinary_account_url(self):
        config = account_config()
        parsed_url = config._parse_cloudinary_url('account://key:secret@test123?foo[bar]=value')
        config._setup_from_parsed_url(parsed_url)
        foo = config.__dict__.get('foo')
        self.assertIsNotNone(foo)
        self.assertEqual(foo.get('bar'), 'value')

    def test_cloudinary_account_url_valid_scheme(self):
        config = account_config()
        cloudinary_account_urls = [
            'account://123456789012345:ALKJdjklLJAjhkKJ45hBK92baj3@test'
            'aCCouNT://123456789012345:ALKJdjklLJAjhkKJ45hBK92baj3@test'
        ]
        for cloudinary_account_url in cloudinary_account_urls:
            parsed_url = config._parse_cloudinary_url(cloudinary_account_url)
            config._setup_from_parsed_url(parsed_url)

    def test_cloudinary_account_url_invalid_scheme(self):
        config = account_config()
        cloudinary_account_urls = [
            'CLOUDINARY__ACCOUNT_URL=account://123456789012345:ALKJdjklLJAjhkKJ45hBK92baj3@test',
            'https://123456789012345:ALKJdjklLJAjhkKJ45hBK92baj3@test',
            '://123456789012345:ALKJdjklLJAjhkKJ45hBK92baj3@test',
            'https://123456789012345:ALKJdjklLJAjhkKJ45hBK92baj3@test?account=foo'
            ' '
        ]
        for cloudinary_account_url in cloudinary_account_urls:
            with self.assertRaises(ValueError):
                parsed_url = config._parse_cloudinary_url(cloudinary_account_url)
                config._setup_from_parsed_url(parsed_url)

    def test_support_CLOUDINARY_prefixed_environment_variables(self):
        os.environ["CLOUDINARY_CLOUD_NAME"] = "c"
        os.environ["CLOUDINARY_API_KEY"] = "k"
        os.environ["CLOUDINARY_API_SECRET"] = "s"
        os.environ["CLOUDINARY_SECURE_DISTRIBUTION"] = "sd"
        os.environ["CLOUDINARY_PRIVATE_CDN"] = "false"
        os.environ["CLOUDINARY_SECURE"] = "true"

        config = cloudinary.Config()

        self.assertEqual(config.cloud_name, "c")
        self.assertEqual(config.api_key, "k")
        self.assertEqual(config.api_secret, "s")
        self.assertEqual(config.secure_distribution, "sd")
        self.assertFalse(config.private_cdn)
        self.assertTrue(config.secure)

    def test_overwrites_only_existing_keys_from_environment(self):
        os.environ["CLOUDINARY_CLOUD_NAME"] = "c"
        os.environ["CLOUDINARY_API_KEY"] = "key_from_env"

        with mock.patch('cloudinary.import_django_settings', return_value=MOCKED_SETTINGS):
            config = cloudinary.Config()

            self.assertEqual(config.cloud_name, "c")
            self.assertEqual(config.api_key, "key_from_env")
            self.assertEqual(config.api_secret, "secret_from_settings")
