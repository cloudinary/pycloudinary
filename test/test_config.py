from unittest import TestCase

import cloudinary


class TestConfig(TestCase):
    def test_parse_cloudinary_url(self):
        config = cloudinary.Config()
        config._parse_cloudinary_url('cloudinary://key:secret@test123?foo[bar]=value')
        foo = config.__dict__.get('foo')
        self.assertIsNotNone(foo)
        self.assertEqual(foo.get('bar'), 'value')

    def test_cloudinary_url_valid_scheme(self):
        config = cloudinary.Config()
        cloudinary_url = 'cloudinary://123456789012345:ALKJdjklLJAjhkKJ45hBK92baj3@test'
        config._parse_cloudinary_url(cloudinary_url)

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
                config._parse_cloudinary_url(cloudinary_url)
