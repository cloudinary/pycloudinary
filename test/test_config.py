from unittest import TestCase

import cloudinary
from cloudinary.provisioning import account_config


class TestConfig(TestCase):
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
