import os

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from cloudinary import api, CloudinaryResource
from cloudinary.forms import CloudinaryFileField
from django_tests.test_helper import SUFFIX

API_TEST_ID = "dj_test_{}".format(SUFFIX)

TEST_IMAGES_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "tests")
TEST_IMAGE = os.path.join(TEST_IMAGES_PATH, "logo.png")


class TestCloudinaryFileField(TestCase):
    def setUp(self):
        with open(TEST_IMAGE, 'rb') as test_image_file:
            self.test_file = SimpleUploadedFile("logo.png", test_image_file.read())

    def test_to_python(self):
        cff_no_auto_save = CloudinaryFileField(autosave=False)
        res = cff_no_auto_save.to_python(None)
        self.assertIsNone(res)
        # without auto_save File is untouched
        res = cff_no_auto_save.to_python(self.test_file)
        self.assertIsInstance(res, SimpleUploadedFile)
        # when auto_save is used, resource is uploaded to Cloudinary and CloudinaryResource is returned
        cff_auto_save = CloudinaryFileField(autosave=True, options={"public_id": API_TEST_ID})
        res = cff_auto_save.to_python(self.test_file)
        self.assertIsInstance(res, CloudinaryResource)
        self.assertEqual(API_TEST_ID, res.public_id)

    def tearDown(self):
        api.delete_resources([API_TEST_ID])
