import random

import cloudinary
from cloudinary import CloudinaryResource
from cloudinary import uploader, api
from django.test import TestCase

from urllib3 import disable_warnings

from .test_helper import SUFFIX

disable_warnings()

TEST_IMAGE = "tests/logo.png"
TEST_TAG = "dj_pycloudinary_test_{0}".format(SUFFIX)


class TestCloudinaryResource(TestCase):
    @classmethod
    def setUpClass(cls):
        cloudinary.reset_config()
        cls.uploaded = uploader.upload(TEST_IMAGE, tags=TEST_TAG)

    @classmethod
    def tearDownClass(cls):
        api.delete_resources_by_tag(TEST_TAG)

    def test_empty_class(self):
        """An empty CloudinaryResource"""

        self.shortDescription()
        res = CloudinaryResource()
        self.assertFalse(res, "should be 'False'")
        self.assertEqual(len(res), 0, "should have zero len()")
        self.assertIsNone(res.url, "should have None url")

    def test_validate(self):
        res = CloudinaryResource(metadata=self.uploaded)
        self.assertTrue(res.validate())
        self.assertTrue(res)
        self.assertGreater(len(res), 0)

    def test_get_prep_value(self):
        res = CloudinaryResource(metadata=self.uploaded)
        value = "image/upload/v{version}/{id}.{format}".format(version=self.uploaded["version"],
                                                               id=self.uploaded["public_id"],
                                                               format=self.uploaded["format"])
        self.assertEqual(value, res.get_prep_value())

    def test_get_presigned(self):
        res = CloudinaryResource(metadata=self.uploaded)
        value = "image/upload/v{version}/{id}.{format}#{signature}".format(version=self.uploaded["version"],
                                                                           id=self.uploaded["public_id"],
                                                                           format=self.uploaded["format"],
                                                                           signature=self.uploaded["signature"])
        self.assertEqual(value, res.get_presigned())

    def test_url(self):
        res = CloudinaryResource(metadata=self.uploaded)
        self.assertEqual(res.url, self.uploaded["url"])

    def test_image(self):
        res = CloudinaryResource(metadata=self.uploaded)
        image = res.image()
        self.assertRegexpMatches(image, '[^-]src="{url}'.format(url=res.url))
        self.assertNotRegexpMatches(image, 'data-src="{url}'.format(url=res.url))
        image = res.image(responsive=True, width="auto", crop="scale")
        self.assertNotRegexpMatches(image, '[^-]src="{url}'.format(url=res.build_url(width="auto", crop="scale")))
        self.assertRegexpMatches(image, 'data-src="{url}'.format(url=res.build_url(width="auto", crop="scale")))

