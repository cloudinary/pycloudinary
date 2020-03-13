from unittest import TestCase

import cloudinary


class TestConfig(TestCase):
    def test_parse_cloudinary_url(self):
        config = cloudinary.Config()
        parsed_url = config._parse_cloudinary_url('cloudinary://key:secret@test123?foo[bar]=value')
        config._setup_from_parsed_url(parsed_url)
        foo = config.__dict__.get('foo')
        self.assertIsNotNone(foo)
        self.assertEqual(foo.get('bar'), 'value')

    def test_cloudinary_url_valid_scheme(self):
        config = cloudinary.Config()
        cloudinary_url = 'cloudinary://123456789012345:ALKJdjklLJAjhkKJ45hBK92baj3@test'
        parsed_url = config._parse_cloudinary_url(cloudinary_url)
        config._setup_from_parsed_url(parsed_url)

    def test_cloudinary_url_invalid_scheme(self):
        config = cloudinary.Config()
        cloudinary_urls = [
            'CLOUDINARY_URL=cloudinary://123456789012345:ALKJdjklLJAjhkKJ45hBK92baj3@test',
            'https://123456789012345:ALKJdjklLJAjhkKJ45hBK92baj3@test',
            '://123456789012345:ALKJdjklLJAjhkKJ45hBK92baj3@test',
            ' '
        ]
        for cloudinary_url in cloudinary_urls:
            with self.assertRaises(ValueError):
                parsed_url = config._parse_cloudinary_url(cloudinary_url)
                config._setup_from_parsed_url(parsed_url)
