from unittest import TestCase

import cloudinary


class TestConfig(TestCase):
    def test_parse_cloudinary_url(self):
        config = cloudinary.Config()
        config._parse_cloudinary_url('cloudinary://key:secret@test123?foo[bar]=value')
        foo = config.__dict__.get('foo')
        self.assertIsNotNone(foo)
        self.assertEqual(foo.get('bar'), 'value')
