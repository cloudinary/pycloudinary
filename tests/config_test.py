from unittest import TestCase

import cloudinary


class TestConfig(TestCase):
    def test_parse_cloudinary_url(self):
        config = cloudinary.Config()
        config._parse_cloudinary_url('cloudinary://key:secret@test123?foo[bar]=value')
        self.assertDictContainsSubset({'foo': {'bar': 'value'}}, config.__dict__)
