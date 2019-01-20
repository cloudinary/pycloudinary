from unittest import TestCase

import mock
from urllib3 import disable_warnings

import cloudinary
from cloudinary import CloudinaryResource
from cloudinary import uploader
from test.helper_test import SUFFIX, TEST_IMAGE, http_response_mock, get_request_url, cleanup_test_resources_by_tag

disable_warnings()

TEST_TAG = "pycloudinary_resource_test_{0}".format(SUFFIX)
TEST_ID = TEST_TAG


class TestCloudinaryResource(TestCase):
    mocked_response = http_response_mock('{"breakpoints": [50, 500, 1000]}')
    mocked_breakpoints = [50, 500, 1000]
    expected_transformation = "c_scale,w_auto:breakpoints_50_1000_20_20:json"

    crop_transformation = {'crop': 'crop', 'width': 100}
    crop_transformation_str = 'c_crop,w_100'

    @classmethod
    def setUpClass(cls):
        cloudinary.reset_config()
        cls.uploaded = uploader.upload(TEST_IMAGE, public_id=TEST_ID, tags=TEST_TAG)

    @classmethod
    def tearDownClass(cls):
        cleanup_test_resources_by_tag([(TEST_TAG,)])

    def setUp(self):
        self.res = CloudinaryResource(metadata=self.uploaded)

    def test_empty_class(self):
        """An empty CloudinaryResource"""

        self.shortDescription()
        res = CloudinaryResource()
        self.assertFalse(res, "should be 'False'")
        self.assertEqual(len(res), 0, "should have zero len()")
        self.assertIsNone(res.url, "should have None url")

    def test_validate(self):
        self.assertTrue(self.res.validate())
        self.assertTrue(self.res)
        self.assertGreater(len(self.res), 0)

    def test_get_prep_value(self):
        value = "image/upload/v{version}/{id}.{format}".format(
            version=self.uploaded["version"],
            id=self.uploaded["public_id"],
            format=self.uploaded["format"])

        self.assertEqual(value, self.res.get_prep_value())

    def test_get_presigned(self):
        value = "image/upload/v{version}/{id}.{format}#{signature}".format(
            version=self.uploaded["version"],
            id=self.uploaded["public_id"],
            format=self.uploaded["format"],
            signature=self.uploaded["signature"])

        self.assertEqual(value, self.res.get_presigned())

    def test_url(self):
        self.assertEqual(self.res.url, self.uploaded["url"])

    def test_image(self):
        image = self.res.image()
        self.assertIn(' src="{url}'.format(url=self.res.url), image)
        self.assertNotIn('data-src="{url}'.format(url=self.res.url), image)
        image = self.res.image(responsive=True, width="auto", crop="scale")
        self.assertNotIn(' src="{url}'.format(url=self.res.build_url(width="auto", crop="scale")), image)
        self.assertIn('data-src="{url}'.format(url=self.res.build_url(width="auto", crop="scale")), image)

    @mock.patch('urllib3.request.RequestMethods.request', return_value=mocked_response)
    def test_fetch_breakpoints(self, mocked_request):
        """Should retrieve responsive breakpoints from cloudinary resource (mocked)"""
        actual_breakpoints = self.res._fetch_breakpoints()

        self.assertEqual(self.mocked_breakpoints, actual_breakpoints)

        self.assertIn(self.expected_transformation, get_request_url(mocked_request))

    @mock.patch('urllib3.request.RequestMethods.request', return_value=mocked_response)
    def test_fetch_breakpoints_with_transformation(self, mocked_request):
        """Should retrieve responsive breakpoints from cloudinary resource with custom transformation (mocked)"""
        srcset = {"transformation": self.crop_transformation}
        actual_breakpoints = self.res._fetch_breakpoints(srcset)

        self.assertEqual(self.mocked_breakpoints, actual_breakpoints)

        self.assertIn(self.crop_transformation_str + "/" + self.expected_transformation,
                      get_request_url(mocked_request))

    def test_fetch_breakpoints_real(self):
        """Should retrieve responsive breakpoints from cloudinary resource (real request)"""
        actual_breakpoints = self.res._fetch_breakpoints()

        self.assertIsInstance(actual_breakpoints, list)

        self.assertGreater(len(actual_breakpoints), 0)
