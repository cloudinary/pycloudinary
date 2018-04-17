import os

from mock import mock

import cloudinary
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from cloudinary import api, CloudinaryResource
from cloudinary.forms import CloudinaryFileField
from django_tests.test_helper import SUFFIX

API_TEST_ID = "dj_test_{}".format(SUFFIX)

TEST_IMAGES_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "tests")
TEST_IMAGE = os.path.join(TEST_IMAGES_PATH, "logo.png")
TEST_IMAGE_W = 241
TEST_IMAGE_H = 51


class TestCloudinaryFileField(TestCase):
    def setUp(self):
        self.test_file = SimpleUploadedFile(TEST_IMAGE, b'content')

    def test_to_python(self):
        cff_no_auto_save = CloudinaryFileField(autosave=False)
        res = cff_no_auto_save.to_python(None)
        self.assertIsNone(res)
        # without auto_save File is untouched
        res = cff_no_auto_save.to_python(self.test_file)
        self.assertIsInstance(res, SimpleUploadedFile)
        # when auto_save is used, resource is uploaded to Cloudinary and CloudinaryResource is returned
        cff_auto_save = CloudinaryFileField(autosave=True, options={"public_id": API_TEST_ID})
        mocked_resource = cloudinary.CloudinaryResource(metadata={"width": TEST_IMAGE_W, "height": TEST_IMAGE_H},
                                                        type="upload", public_id=API_TEST_ID, resource_type="image")

        with mock.patch('cloudinary.uploader.upload_image', return_value=mocked_resource) as upload_mock:
            res = cff_auto_save.to_python(self.test_file)

        self.assertTrue(upload_mock.called)
        self.assertIsInstance(res, CloudinaryResource)
        self.assertEqual(API_TEST_ID, res.public_id)

    def tearDown(self):
        pass
